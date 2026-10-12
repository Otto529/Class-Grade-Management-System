# -*- coding: utf-8 -*-
"""对 pymysql 的简单封装，查询结果直接返回字典，省得记字段下标。"""
import pymysql
from pymysql.cursors import DictCursor

from config import DB_CONFIG

_conn_cfg = dict(DB_CONFIG)
_conn_cfg["cursorclass"] = DictCursor


def get_connection():
    return pymysql.connect(**_conn_cfg)


def query(sql, args=None):
    # 查多条
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchall()
    finally:
        conn.close()


def query_one(sql, args=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchone()
    finally:
        conn.close()


def execute(sql, args=None):
    # 单条增删改，返回新插入的 id
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            n = cur.execute(sql, args or ())
            conn.commit()
            return cur.lastrowid if n else 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def executemany(sql, args_seq):
    # 批量写入用，比循环 execute 快很多
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            n = cur.executemany(sql, args_seq)
            conn.commit()
            return n
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def transaction(fn):
    # 需要多条 sql 一起提交/回滚的时候用
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            result = fn(cur)
            conn.commit()
            return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
