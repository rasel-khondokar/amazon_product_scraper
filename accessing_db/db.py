import pandas as pd
import mysql.connector
from settings import BASE_DIR, TABLE_NAME_KEYWORDS


class DBConnector():
    allow_local_infile = True
    def __init__(self, credential, host, port):
        self.credential = credential
        self.host = host
        self.port = port

    def connect(self, dbname=None):
        self.dbname=dbname
        if dbname:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.credential['username'],
                password=self.credential['password'],
                database=self.dbname,
                allow_local_infile= self.allow_local_infile
            )
        else:
            self.connection = mysql.connector.connect(
                host='localhost',
                user=self.credential['username'],
                password=self.credential['password'],
                allow_local_infile=self.allow_local_infile
            )
        self.global_foreign_key_check(False)
        return self.connection

    def close(self):
        if (self.connection.is_connected()):
            self.connection.close()
            # print("MySQL connection is closed")
        else:
            print("MySQL is not connected!")

    def global_foreign_key_check(self, check):
        if check:
            sql = 'SET GLOBAL FOREIGN_KEY_CHECKS=1;'
        else:
            sql = 'SET GLOBAL FOREIGN_KEY_CHECKS=0;'
        mycursor = self.connection.cursor()
        mycursor.execute(f"{sql}")

    def create_database(self, dbname):
        mycursor = self.connection.cursor()
        mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbname}")
        print(f'{dbname} database created!')
        self.connection = self.connect(dbname)

    def get_columns(self, tbname):
        mycursor = self.connection.cursor()
        mycursor.execute(f'SHOW columns FROM {tbname};')
        columns = mycursor.fetchall()
        return columns

    def get_tables(self):
        mycursor = self.connection.cursor()
        mycursor.execute("SHOW TABLES;")
        tables = mycursor.fetchall()
        return tables

    def check_table_existence(self, table_name):
        tables = self.get_tables()
        for table in tables:
            if table[0] == table_name:
                return True

    def create_table(self, tbname, columns, charset, relationship=''):
        if not self.check_table_existence(tbname):
            mycursor = self.connection.cursor()
            try:
                sql = f"CREATE TABLE IF NOT EXISTS {tbname} ({columns} {relationship}) CHARACTER SET {charset};"
                mycursor.execute(sql)
                print(f'{tbname} table created!')
            except mysql.connector.Error as err:
                print(err.errno)
                print(err.msg)

    def save_data(self, cursor, sql, tbname, data):
        cursor.execute(sql, data)
        self.connection.commit()
        saved_msg = f"{cursor.rowcount} row saved to {tbname} table of {self.dbname} database."
        saved_count = cursor.rowcount
        return saved_count, saved_msg

    def show_foreign_key_check(self):
        mycursor = self.connection.cursor(dictionary=True)
        mycursor.execute(f"SHOW Variables WHERE Variable_name='foreign_key_checks';")
        result = mycursor.fetchall()
        status = f"{result[0]['Variable_name']} {result[0]['Value']}"
        print(status)

    def save_to_table(self, tbname, data=dict()):
        saved_count = 0
        # self.show_foreign_key_check()
        for key, value in list(data.items()):
            if value == None:
                del data[key]

        prepared_data = data

        fields = ','.join(list(map(lambda x: '`' + x + '`', [*prepared_data.keys()])))
        values = ','.join(list(map(lambda x: '%(' + x + ')s', [*prepared_data.keys()])))
        sql = "INSERT INTO `%s` (%s) VALUES (%s)" % (tbname, fields, values)

        try:
            mycursor = self.connection.cursor()
            saved_count, saved_msg = self.save_data(mycursor, sql, tbname, prepared_data)
            result = saved_msg
        except mysql.connector.IntegrityError as err:
            if err.errno == 1452:
                self.global_foreign_key_check(False)
                self.show_foreign_key_check()
                mycursor = self.connection.cursor()
                saved_count, saved_msg = self.save_data(mycursor, sql, tbname, prepared_data)
                result = saved_msg
            else:
                result = err.msg
        except mysql.connector.Error as err:
            result = err.msg
        return saved_count, result

    def get_data_from_columns(self, tbname, params=None, columns=None, unique=False):
        if unique:
            distinct = 'distinct'
        else:
            distinct = ''

        if columns:
            columns = ', '.join(columns)
        else:
            columns = '*'
        if params:
            params_str = f''
            params_index_last = len(params)-1
            for count, ky in enumerate(params):
                params_values = params[ky].replace("'", "''")
                if count != params_index_last:
                    params_str = params_str + f"{ky} = '{params_values}' and "
                else:
                    params_str = params_str +f"{ky} = '{params_values}'"

            sql_query_data = f"select {distinct} {columns} from {tbname} where {params_str};"
        else:
            sql_query_data = f"select {distinct} {columns} from {tbname};"
        mycursor = self.connection.cursor(dictionary=True)
        sql_query_data = u'{}'.format(sql_query_data)
        mycursor.execute(sql_query_data)
        data = mycursor.fetchall()
        return data

    def get_keywords(self):
        return self.get_data_from_columns(TABLE_NAME_KEYWORDS)