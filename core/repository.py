# -*- coding: utf-8 -*-
"""
sql 基本都放这个文件里。
排名和统计没有用「先查学生再一个个查成绩」的写法，那样查询次数太多，
都是一条 join 查出来，配合 init.sql 里的复合索引。
"""
from core import database as db


# 几个下拉框要用的数据
def list_classes():
    return db.query("SELECT * FROM classes ORDER BY id")


def list_subjects():
    return db.query("SELECT * FROM subjects ORDER BY sort_no, id")


def list_exams():
    return db.query("SELECT * FROM exams ORDER BY exam_date DESC, id DESC")


# 学生
def list_students(class_id=None, keyword=None):
    sql = """
        SELECT s.id, s.student_no, s.name, s.gender, s.status,
               s.class_id, c.class_name
        FROM students s
        JOIN classes c ON c.id = s.class_id
        WHERE 1=1
    """
    args = []
    if class_id:
        sql += " AND s.class_id = %s"
        args.append(class_id)
    if keyword:
        sql += " AND (s.name LIKE %s OR s.student_no LIKE %s)"
        args += [f"%{keyword}%", f"%{keyword}%"]
    sql += " ORDER BY s.student_no"
    return db.query(sql, args)


def get_student(student_id):
    return db.query_one("SELECT * FROM students WHERE id=%s", (student_id,))


def save_student(student_no, name, gender, class_id, student_id=None):
    if student_id:
        db.execute(
            "UPDATE students SET student_no=%s,name=%s,gender=%s,class_id=%s WHERE id=%s",
            (student_no, name, gender, class_id, student_id),
        )
    else:
        return db.execute(
            "INSERT INTO students(student_no,name,gender,class_id) VALUES(%s,%s,%s,%s)",
            (student_no, name, gender, class_id),
        )


def delete_student(student_id):
    db.execute("DELETE FROM students WHERE id=%s", (student_id,))


# 成绩录入页：把这个班的学生和已有成绩一次查出来填进表格
def score_entry_grid(exam_id, class_id):
    students = db.query(
        """SELECT id, student_no, name FROM students
           WHERE class_id=%s AND status=1 ORDER BY student_no""",
        (class_id,),
    )
    subjects = list_subjects()
    rows = db.query(
        """SELECT sc.student_id, sc.subject_id, sc.score
           FROM scores sc
           JOIN students st ON st.id = sc.student_id
           WHERE sc.exam_id=%s AND st.class_id=%s""",
        (exam_id, class_id),
    )
    score_map = {(r["student_id"], r["subject_id"]): float(r["score"])
                 for r in rows if r["score"] is not None}
    grid = []
    for st in students:
        row = {"student_id": st["id"], "student_no": st["student_no"], "name": st["name"],
               "scores": [score_map.get((st["id"], su["id"])) for su in subjects]}
        grid.append(row)
    return subjects, grid


def bulk_upsert_scores(exam_id, records):
    # 成绩批量保存，已存在就覆盖，靠 scores 的唯一键触发 update
    if not records:
        return 0
    placeholders = ",".join(["(%s,%s,%s,%s)"] * len(records))
    flat = [v for r in records for v in r]
    sql = f"""
        INSERT INTO scores(exam_id, student_id, subject_id, score)
        VALUES {placeholders}
        ON DUPLICATE KEY UPDATE score=VALUES(score)
    """
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            n = cur.execute(sql, flat)
            conn.commit()
            return n
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# 各科均分、及格率这些
def subject_stats(exam_id, class_id=None):
    where = "sc.exam_id=%s"
    args = [exam_id]
    if class_id:
        where += " AND st.class_id=%s"
        args.append(class_id)
    return db.query(f"""
        SELECT su.id, su.name, su.full_score,
               COUNT(sc.score)                AS cnt,
               ROUND(AVG(sc.score),2)         AS avg_score,
               ROUND(MAX(sc.score),1)         AS max_score,
               ROUND(MIN(sc.score),1)         AS min_score,
               ROUND(100*SUM(sc.score >= su.full_score*0.6)/COUNT(sc.score),1) AS pass_rate,
               ROUND(100*SUM(sc.score >= su.full_score*0.85)/COUNT(sc.score),1) AS excellent_rate
        FROM scores sc
        JOIN subjects su ON su.id = sc.subject_id
        JOIN students st ON st.id = sc.student_id
        WHERE {where}
        GROUP BY su.id, su.name, su.full_score
        ORDER BY su.sort_no
    """, args)


# 分数段人数，段是按满分比例划的，这样150和100的科目能共用
def score_distribution(exam_id, class_id=None):
    where = "sc.exam_id=%s"
    args = [exam_id]
    if class_id:
        where += " AND st.class_id=%s"
        args.append(class_id)
    return db.query(f"""
        SELECT su.name AS subject,
               SUM(CASE WHEN sc.score <  su.full_score*0.6  THEN 1 ELSE 0 END) AS d0,
               SUM(CASE WHEN sc.score >= su.full_score*0.6 AND sc.score < su.full_score*0.7 THEN 1 ELSE 0 END) AS d1,
               SUM(CASE WHEN sc.score >= su.full_score*0.7 AND sc.score < su.full_score*0.8 THEN 1 ELSE 0 END) AS d2,
               SUM(CASE WHEN sc.score >= su.full_score*0.8 AND sc.score < su.full_score*0.85 THEN 1 ELSE 0 END) AS d3,
               SUM(CASE WHEN sc.score >= su.full_score*0.85 THEN 1 ELSE 0 END) AS d4
        FROM scores sc
        JOIN subjects su ON su.id = sc.subject_id
        JOIN students st ON st.id = sc.student_id
        WHERE {where}
        GROUP BY su.id, su.name
        ORDER BY su.sort_no
    """, args)


# 排名，单科和总分都走这里，名次用 rank()，同分并列
def ranking(exam_id, class_id=None, subject_id=None):
    if subject_id:
        where = "sc.exam_id=%s AND sc.subject_id=%s"
        args = [exam_id, subject_id]
        if class_id:
            where += " AND st.class_id=%s"
            args.append(class_id)
        sql = f"""
            SELECT st.student_no, st.name, c.class_name,
                   ROUND(sc.score,1) AS total,
                   RANK() OVER (ORDER BY sc.score DESC) AS rk
            FROM scores sc
            JOIN students st ON st.id = sc.student_id
            JOIN classes  c  ON c.id = st.class_id
            WHERE {where}
            ORDER BY rk, st.student_no
        """
    else:
        where = "sc.exam_id=%s"
        args = [exam_id]
        if class_id:
            where += " AND st.class_id=%s"
            args.append(class_id)
        sql = f"""
            SELECT st.student_no, st.name, c.class_name,
                   COUNT(sc.score)                AS subject_cnt,
                   ROUND(SUM(sc.score),1)         AS total,
                   ROUND(AVG(sc.score),2)         AS avg_score,
                   RANK() OVER (ORDER BY SUM(sc.score) DESC) AS rk
            FROM scores sc
            JOIN students st ON st.id = sc.student_id
            JOIN classes  c  ON c.id = st.class_id
            WHERE {where}
            GROUP BY st.id, st.student_no, st.name, c.class_name
            ORDER BY rk, st.student_no
        """
    return db.query(sql, args)


# 导出成绩册用，把学生各科成绩摊成一行
def score_report(exam_id, class_id=None):
    subjects = list_subjects()
    where = "sc.exam_id=%s"
    args = [exam_id]
    if class_id:
        where += " AND st.class_id=%s"
        args.append(class_id)
    rows = db.query(f"""
        SELECT st.student_no, st.name, c.class_name,
               su.name AS subject, sc.score
        FROM scores sc
        JOIN students st ON st.id = sc.student_id
        JOIN classes  c  ON c.id = st.class_id
        JOIN subjects su ON su.id = sc.subject_id
        WHERE {where}
        ORDER BY st.student_no, su.sort_no
    """, args)
    students = {}
    for r in rows:
        key = r["student_no"]
        if key not in students:
            students[key] = {"student_no": key, "name": r["name"],
                             "class_name": r["class_name"],
                             "scores": {su["name"]: None for su in subjects}}
        students[key]["scores"][r["subject"]] = float(r["score"]) if r["score"] is not None else None
    return subjects, list(students.values())


# 工作台上面那几个数字
def dashboard():
    def one(sql):
        return db.query_one(sql)
    return {
        "student_count": one("SELECT COUNT(*) n FROM students WHERE status=1")["n"],
        "class_count": one("SELECT COUNT(*) n FROM classes")["n"],
        "exam_count": one("SELECT COUNT(*) n FROM exams")["n"],
        "score_count": one("SELECT COUNT(*) n FROM scores")["n"],
        "latest_exams": list_exams()[:5],
    }
