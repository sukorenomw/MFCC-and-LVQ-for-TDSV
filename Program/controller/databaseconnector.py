import sqlite3 as sql
import numpy as np
import io

TYPE=2

class DatabaseConnector():
    def __init__(self):
        sql.register_adapter(np.ndarray, self.adapt_array)
        sql.register_converter("array", self.convert_array)
        self.conn = sql.connect('database/features'+str(TYPE)+'.db', isolation_level=None, detect_types=sql.PARSE_DECLTYPES, check_same_thread=False)

        if TYPE == 1:
            self.conn.execute("CREATE TABLE IF NOT EXISTS `files` ("
                              "`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
                              "`file_path` TEXT NOT NULL)")

            self.conn.execute("CREATE TABLE IF NOT EXISTS `features` ("
                              "`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
                              "`file_id` INTEGER NOT NULL,"
                              "`frame` INTEGER NOT NULL,"
                              "`feature` array NOT NULL,"
                              "`class` TEXT NOT NULL)")

        else:
            self.conn.execute("CREATE TABLE IF NOT EXISTS `output_classes` ("
                              "`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
                              "`file_path` TEXT NOT NULL,"
                              "`class` TEXT NOT NULL)")

            self.conn.execute("CREATE TABLE IF NOT EXISTS `feature_sets` ("
                              "`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
                              "`output_class_id` INTEGER NOT NULL,"
                              "`frame` INTEGER NOT NULL,"
                              "`features` array NOT NULL)")

    def close(self):
        self.conn.close()

    def insert_features(self, arg):
        cur = self.conn.cursor()
        if TYPE == 1:
            cur.executemany("INSERT INTO features (file_id, frame, feature, class) VALUES (?,?,?,?)", (arg))
        else:
            cur.executemany("INSERT INTO feature_sets (output_class_id, frame, features) VALUES (?,?,?)", (arg))
        return cur.lastrowid

    def insert(self, table, params):
        key = []
        values = []
        for i,k in enumerate(sorted(params)):
            key.append(k)
            values.append(params[k])

        cur = self.conn.cursor()
        cur.execute("INSERT INTO " + str(table) + " (" + ",".join(key) + ") VALUES ('" + "', '".join(map(str, values)) + "')")
        return cur.lastrowid

    def select(self, table, clause=None):
        with self.conn:
            self.conn.row_factory = sql.Row
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM "+table+self.whereClause(clause))

        return cur.fetchall()

    def select_group(self, table, group):
        with self.conn:
            self.conn.row_factory = sql.Row
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM "+table+" GROUP BY "+group)

        return cur.fetchall()

    def select_one(self, table, clause=None):
        with self.conn:
            self.conn.row_factory = sql.Row
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM " + table + self.whereClause(clause))

        return cur.fetchone()

    def update(self, table, params, clause = None):
        strings = []
        for i, k in enumerate(sorted(params)):
            strings.append(k + " = '" + params[k]+"'")

        self.conn.execute("UPDATE "+table+ " SET "+", ".join(map(str,strings))+self.whereClause(clause))

    def delete(self, table, clause=None):
        self.conn.execute("DELETE FROM "+table+self.whereClause(clause))

    def whereClause(self, params=None):
        if params is None:
            return ''

        strings = []
        for i,k in enumerate(sorted(params)):
            strings.append(k+" = '"+params[k]+"'")

        return " WHERE "+" AND ".join(map(str,strings))

    def adapt_array(self,arr):
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)
        return sql.Binary(out.read())

    def convert_array(self,text):
        out = io.BytesIO(text)
        out.seek(0)
        return np.load(out)