# -*- coding: utf-8 -*-
"""
flask 主程序，启动后访问 http://127.0.0.1:5000
"""
from flask import (Flask, jsonify, redirect, render_template, request,
                   send_file, url_for)

import config
from core import excel_utils, repository as repo

app = Flask(__name__)
app.config.from_object(config)


# 页面
@app.route("/")
def page_dashboard():
    return render_template("dashboard.html", data=repo.dashboard())


@app.route("/students")
def page_students():
    class_id = request.args.get("class_id", type=int)
    keyword = request.args.get("keyword", type=str)
    students = repo.list_students(class_id or None, keyword)
    return render_template("students.html", students=students,
                           classes=repo.list_classes(),
                           cur_class=class_id, keyword=keyword or "")


@app.route("/scores")
def page_scores():
    exams = repo.list_exams()
    classes = repo.list_classes()
    exam_id = request.args.get("exam_id", exams[0]["id"] if exams else None, type=int)
    class_id = request.args.get("class_id", classes[0]["id"] if classes else None, type=int)
    subjects, grid = [], []
    if exam_id and class_id:
        subjects, grid = repo.score_entry_grid(exam_id, class_id)
    return render_template("scores.html", exams=exams, classes=classes,
                           subjects=subjects, grid=grid,
                           exam_id=exam_id, class_id=class_id)


@app.route("/stats")
def page_stats():
    exams = repo.list_exams()
    classes = repo.list_classes()
    return render_template("stats.html", exams=exams, classes=classes)


@app.route("/ranking")
def page_ranking():
    exams = repo.list_exams()
    classes = repo.list_classes()
    subjects = repo.list_subjects()
    return render_template("ranking.html", exams=exams, classes=classes,
                           subjects=subjects)


# 学生增删改
@app.post("/api/students/save")
def api_student_save():
    p = request.get_json(force=True)
    try:
        repo.save_student(p["student_no"], p["name"], p.get("gender", "男"),
                          int(p["class_id"]), p.get("id"))
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, msg=f"保存失败：{e}"), 400


@app.post("/api/students/delete")
def api_student_delete():
    repo.delete_student(int(request.get_json(force=True)["id"]))
    return jsonify(ok=True)


# 班级
@app.post("/api/classes/save")
def api_class_save():
    p = request.get_json(force=True)
    if p.get("id"):
        repo.db.execute("UPDATE classes SET class_name=%s,grade=%s WHERE id=%s",
                        (p["class_name"], p.get("grade"), p["id"]))
    else:
        repo.db.execute("INSERT INTO classes(class_name,grade) VALUES(%s,%s)",
                        (p["class_name"], p.get("grade")))
    return jsonify(ok=True)


@app.post("/api/classes/delete")
def api_class_delete():
    try:
        repo.db.execute("DELETE FROM classes WHERE id=%s",
                        (int(request.get_json(force=True)["id"]),))
        return jsonify(ok=True)
    except Exception:
        # 班里还有学生的时候外键会拦，给前端个提示
        return jsonify(ok=False, msg="该班级下仍有学生，无法删除"), 400


# 科目
@app.post("/api/subjects/save")
def api_subject_save():
    p = request.get_json(force=True)
    if p.get("id"):
        repo.db.execute("UPDATE subjects SET name=%s,full_score=%s WHERE id=%s",
                        (p["name"], p["full_score"], p["id"]))
    else:
        repo.db.execute("INSERT INTO subjects(name,full_score) VALUES(%s,%s)",
                        (p["name"], p["full_score"]))
    return jsonify(ok=True)


# 考试，新增和编辑都走这个
@app.post("/api/exams/save")
def api_exam_save():
    p = request.get_json(force=True)
    if p.get("id"):
        repo.db.execute(
            "UPDATE exams SET name=%s,exam_date=%s,remark=%s WHERE id=%s",
            (p["name"], p.get("exam_date") or None, p.get("remark"), p["id"]))
    else:
        repo.db.execute("INSERT INTO exams(name,exam_date,remark) VALUES(%s,%s,%s)",
                        (p["name"], p.get("exam_date") or None, p.get("remark")))
    return jsonify(ok=True)


@app.post("/api/exams/delete")
def api_exam_delete():
    repo.db.execute("DELETE FROM exams WHERE id=%s",
                    (int(request.get_json(force=True)["id"]),))
    return jsonify(ok=True)


# 成绩录入页点保存
@app.post("/api/scores/save")
def api_scores_save():
    p = request.get_json(force=True)
    exam_id = int(p["exam_id"])
    records = []
    for item in p["items"]:
        sid = int(item["student_id"])
        for sub in item["rows"]:
            val = sub.get("score")
            if val is None or val == "":
                continue
            records.append((exam_id, sid, int(sub["subject_id"]), float(val)))
    n = repo.bulk_upsert_scores(exam_id, records)
    return jsonify(ok=True, count=n)


# 统计页要的数据
@app.get("/api/stats")
def api_stats():
    exam_id = request.args.get("exam_id", type=int)
    class_id = request.args.get("class_id", type=int)
    return jsonify(subjects=repo.subject_stats(exam_id, class_id or None),
                   distribution=repo.score_distribution(exam_id, class_id or None))


# 排名页要的数据
@app.get("/api/ranking")
def api_ranking():
    exam_id = request.args.get("exam_id", type=int)
    class_id = request.args.get("class_id", type=int)
    subject_id = request.args.get("subject_id", type=int)
    return jsonify(rows=repo.ranking(exam_id, class_id or None,
                                     subject_id or None))


# 模板下载
@app.get("/template/students")
def tpl_students():
    return send_file(excel_utils.student_template(), as_attachment=True,
                     download_name="学生名单模板.xlsx")


@app.get("/template/scores")
def tpl_scores():
    return send_file(excel_utils.score_template(), as_attachment=True,
                     download_name="成绩录入模板.xlsx")


# excel 导入
@app.post("/import/students")
def import_students():
    f = request.files.get("file")
    n, errors = excel_utils.import_students(f.stream)
    return jsonify(ok=True, count=n, errors=errors)


@app.post("/import/scores")
def import_scores():
    exam_id = int(request.form["exam_id"])
    f = request.files.get("file")
    n, errors = excel_utils.import_scores(f.stream, exam_id)
    return jsonify(ok=True, count=n, errors=errors)


# 导出成绩册
@app.get("/export/report")
def export_report():
    exam_id = request.args.get("exam_id", type=int)
    class_id = request.args.get("class_id", type=int)
    fname, buf = excel_utils.export_report(exam_id, class_id or None)
    return send_file(buf, as_attachment=True, download_name=fname)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
