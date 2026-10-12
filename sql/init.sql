-- 班级成绩管理系统建表脚本，MySQL8 下跑
DROP DATABASE IF EXISTS grade_system;
CREATE DATABASE grade_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE grade_system;

-- 班级
CREATE TABLE classes (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    class_name  VARCHAR(50)  NOT NULL COMMENT '班级名称，如高三(1)班',
    grade       VARCHAR(20)  DEFAULT NULL COMMENT '年级',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_class_name (class_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级表';

-- 学生
CREATE TABLE students (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    student_no  VARCHAR(20)  NOT NULL COMMENT '学号',
    name        VARCHAR(30)  NOT NULL COMMENT '姓名',
    gender      ENUM('男','女') NOT NULL DEFAULT '男',
    class_id    INT UNSIGNED NOT NULL,
    status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1在读 0不在校',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_student_no (student_no),
    KEY idx_students_class (class_id),
    KEY idx_students_name (name),
    CONSTRAINT fk_students_class FOREIGN KEY (class_id) REFERENCES classes (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生表';

-- 科目
CREATE TABLE subjects (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        VARCHAR(30)  NOT NULL COMMENT '科目名，如语文',
    full_score  DECIMAL(5,1) NOT NULL DEFAULT 100.0 COMMENT '满分',
    sort_no     INT          NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_subject_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='科目表';

-- 考试
CREATE TABLE exams (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        VARCHAR(50)  NOT NULL COMMENT '考试名称',
    exam_date   DATE         DEFAULT NULL,
    remark      VARCHAR(200) DEFAULT NULL COMMENT '备注',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_exams_date (exam_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考试表';

-- 成绩，数据量最大的一张表
CREATE TABLE scores (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    exam_id     INT UNSIGNED NOT NULL,
    student_id  INT UNSIGNED NOT NULL,
    subject_id  INT UNSIGNED NOT NULL,
    score       DECIMAL(5,1) DEFAULT NULL COMMENT '成绩，缺考为空',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    -- 同一场考试同一个学生同一科只能有一条，防止录重
    UNIQUE KEY uk_score (exam_id, student_id, subject_id),
    -- 这两个索引是给统计和排名用的，score 放里面可以少回一次表
    KEY idx_exam_subject (exam_id, subject_id, score),
    KEY idx_exam_student (exam_id, student_id, subject_id, score),
    CONSTRAINT fk_scores_exam    FOREIGN KEY (exam_id)    REFERENCES exams (id)    ON DELETE CASCADE,
    CONSTRAINT fk_scores_student FOREIGN KEY (student_id) REFERENCES students (id),
    CONSTRAINT fk_scores_subject FOREIGN KEY (subject_id) REFERENCES subjects (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成绩表';

-- 基础数据
INSERT INTO classes (class_name, grade) VALUES
('高三(1)班', '2024级'),
('高三(2)班', '2024级');

INSERT INTO subjects (name, full_score, sort_no) VALUES
('语文', 150, 1),
('数学', 150, 2),
('英语', 150, 3),
('物理', 100, 4),
('化学', 100, 5),
('生物', 100, 6);

INSERT INTO exams (name, exam_date, remark) VALUES
('2026年秋季第一次月考', '2026-09-15', '开学摸底'),
('2026年秋季期中考试',   '2026-10-08', NULL);
