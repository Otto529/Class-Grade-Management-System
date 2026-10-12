# -*- coding: utf-8 -*-
"""配置文件。账号密码不写死在代码里，从环境变量读取（见 README）。"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "grade_system"),
    "charset": "utf8mb4",
    "cursorclass": None,     # database.py 里会换成 DictCursor
    "autocommit": False,
}

# 上传的 Excel 别太大，限 16M
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

SECRET_KEY = os.getenv("SECRET_KEY", "grade-system-dev-secret")
