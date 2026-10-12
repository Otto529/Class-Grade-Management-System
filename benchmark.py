# -*- coding: utf-8 -*-
"""
跑一下排名查询两种写法的耗时对比：
naive 是先查学生再循环查每个人的成绩（n+1），
optimized 是一条 join 加 rank()。
用法：python benchmark.py，后面可以跟轮数，默认30
"""
import statistics
import sys
import time

from core import database as db

ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 30


def naive_ranking(exam_id):
    students = db.query(
        """SELECT st.id, st.student_no, st.name, c.class_name
           FROM students st JOIN classes c ON c.id=st.class_id
           WHERE st.status=1 ORDER BY st.student_no""")
    result = []
    for st in students:
        scores = db.query(
            "SELECT score FROM scores WHERE exam_id=%s AND student_id=%s",
            (exam_id, st["id"]))
        vals = [float(r["score"]) for r in scores if r["score"] is not None]
        if vals:
            result.append((st["student_no"], st["name"], st["class_name"],
                           round(sum(vals), 1)))
    result.sort(key=lambda x: x[3], reverse=True)
    return result


def optimized_ranking(exam_id):
    return db.query("""
        SELECT st.student_no, st.name, c.class_name,
               ROUND(SUM(sc.score),1) AS total,
               RANK() OVER (ORDER BY SUM(sc.score) DESC) AS rk
        FROM scores sc
        JOIN students st ON st.id = sc.student_id
        JOIN classes  c  ON c.id = st.class_id
        WHERE sc.exam_id=%s
        GROUP BY st.id, st.student_no, st.name, c.class_name
        ORDER BY rk
    """, (exam_id,))


def timeit(fn, *args):
    samples = []
    for _ in range(ROUNDS):
        t0 = time.perf_counter()
        fn(*args)
        samples.append((time.perf_counter() - t0) * 1000)
    return statistics.mean(samples), statistics.median(samples)


def main():
    exam = db.query_one("SELECT id,name FROM exams ORDER BY id LIMIT 1")
    exam_id = exam["id"]

    # 先确认两种查出来的第一名总分一样，别比了半天结果不对
    n0 = naive_ranking(exam_id)
    o0 = optimized_ranking(exam_id)
    assert n0[0][3] == float(o0[0]["total"]), "两种写法结果对不上"

    naive_avg, naive_med = timeit(naive_ranking, exam_id)
    opt_avg, opt_med = timeit(optimized_ranking, exam_id)
    gain_avg = (naive_avg - opt_avg) / naive_avg * 100
    gain_med = (naive_med - opt_med) / naive_med * 100

    print("=" * 56)
    print(f"考试：{exam['name']}   轮数：{ROUNDS}")
    print("-" * 56)
    print(f"{'写法':<22}{'平均(ms)':>12}{'中位(ms)':>12}")
    print(f"{'n+1':<22}{naive_avg:>12.3f}{naive_med:>12.3f}")
    print(f"{'join+rank()':<20}{opt_avg:>12.3f}{opt_med:>12.3f}")
    print("-" * 56)
    print(f"快了：平均 {gain_avg:.1f}%   中位 {gain_med:.1f}%")
    print("=" * 56)


if __name__ == "__main__":
    main()
