#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/5/30 15:01
# @Author : chaocai
import sqlite3


def init_db():
    conn = sqlite3.connect('level.db')
    cursor = conn.cursor()
    try:
        cursor.execute('CREATE TABLE Level (Name TEXT, Url TEXT, Level TEXT)')
        cursor.close()
        conn.commit()
        conn.close()
    except:
        pass


def insert(name, url, level):
    conn = sqlite3.connect('level.db')
    cursor = conn.cursor()
    sql = "INSERT INTO Level (Name, Url, Level) VALUES ('%s', '%s', '%s')" % (name, url, level)
    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()


def update(name, level):
    conn = sqlite3.connect('level.db')
    cursor = conn.cursor()
    sql = "UPDATE Level SET Level = '%s' WHERE Name = '%s'" % (level, name)
    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()


def query(name):
    conn = sqlite3.connect('level.db')
    cursor = conn.cursor()
    inset_sql = "SELECT * FROM Level WHERE Name = '%s'" % name
    cursor.execute(inset_sql)
    result = cursor.fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    return result