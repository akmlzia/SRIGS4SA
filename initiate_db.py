import sqlite3
import json

#For insert and get deck and progress dict
sqlite3.register_adapter(dict, lambda d: json.dumps(d).encode('utf8'))
sqlite3.register_converter("json", lambda d: json.loads(d.decode('utf8')))

def initiate_db():
    conn = sqlite3.connect('data.db')
    curs = conn.cursor()
    create_students_table = """ CREATE TABLE IF NOT EXISTS students (
                                id integer PRIMARY KEY,
                                nick_name text NOT NULL,
                                full_name text NOT NULL,
                                group_name text,
                                join_date text NOT NULL
                            );"""
    create_cards_table = """ CREATE TABLE IF NOT EXISTS cards (
                                id integer PRIMARY KEY,
                                front_side text NOT NULL,
                                back_side text NOT NULL
                            );"""
    create_progress_table = """ CREATE TABLE IF NOT EXISTS progress (
                                id integer PRIMARY KEY,
                                student_id integer NOT NULL REFERENCES students(id) ON UPDATE CASCADE ON DELETE CASCADE,
                                progress json NOT NULL
                            );"""

    commands = [create_students_table, create_cards_table, create_progress_table]
    for command in commands:
        curs.execute(command)
    conn.close()