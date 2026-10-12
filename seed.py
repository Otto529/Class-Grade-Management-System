# -*- coding: utf-8 -*-
"""
造点测试数据：两个班各40人，两场考试的成绩。
成绩不是纯随机，按学生水平给个基础分再加波动，看起来正常点。
"""
import random

from core import database as db

SURNAMES = list("王李张刘陈杨赵黄周吴徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭")
GIVEN = list("伟芳娜敏静丽强磊军洋勇艳杰娟涛明超秀兰霞平刚桂英华红建文轩浩宇欣怡子涵梓萱雨桐思远嘉怡梦琪俊杰")

PER_CLASS = 40


def gen_name(used):
    for _ in range(100):
        name = random.choice(SURNAMES) + "".join(random.sample(GIVEN, random.choice((1, 2))))
        if name not in used:
            used.add(name)
            return name
    used.add("同学" + str(len(used)))
    return "同学" + str(len(used))


def main():
    random.seed(20261012)
    classes = db.query("SELECT id FROM classes ORDER BY id")
    subjects = db.query("SELECT id, full_score FROM subjects ORDER BY sort_no")
    exams = db.query("SELECT id FROM exams ORDER BY id")

    used_names = set()
    students = []
    no = 20240101
    for c in classes:
        for _ in range(PER_CLASS):
            students.append((str(no), gen_name(used_names),
                             random.choice(("男", "女")), c["id"]))
            no += 1
    db.executemany(
        "INSERT INTO students(student_no,name,gender,class_id) VALUES(%s,%s,%s,%s)",
        students)
    stu_rows = db.query("SELECT id FROM students ORDER BY id")

    records = []
    for exam in exams:
        for st in stu_rows:
            ability = random.uniform(0.45, 0.98)   # 这个学生的整体水平
            for su in subjects:
                full = float(su["full_score"])
                ratio = min(1.0, max(0.15, ability + random.uniform(-0.12, 0.12)))
                if random.random() < 0.02:
                    score = None                   # 少量缺考
                else:
                    score = round(ratio * full * random.uniform(0.97, 1.03) / 0.5) * 0.5
                    score = min(full, max(0, score))
                records.append((exam["id"], st["id"], su["id"], score))
    db.executemany(
        "INSERT INTO scores(exam_id,student_id,subject_id,score) VALUES(%s,%s,%s,%s)",
        records)
    print(f"完成：学生 {len(students)} 名，成绩 {len(records)} 条")


if __name__ == "__main__":
    main()
