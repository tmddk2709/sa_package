import pymysql
import pymysql.cursors
import pandas as pd


class MySQLConnection:

    def __init__(self, host, port, db, user, password, scheme):

        self.__host = host
        self.__port = port
        self.__db = db
        self.__user = user
        self.__password = password
        self.__scheme = scheme

        self.__connection = pymysql.connect(
            host=self.__host,
            port=self.__port,
            user=self.__user,
            password=self.__password,
            db=self.__db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )


    def get_conenction(self):

        return self.__connection


    def execute_sql(self, sql):

        cursor = self.__connection.cursor()

        try:
            cursor.execute(sql)
            self.__connection.commit()
        except Exception as e:
            print(e)
        finally:
            self.__connection.close()


    def get_data(self, sql):
        """
        get data as pd.DataFrame() type from database
        """

        try:
            data = pd.read_sql(sql, con=self.__connection)
        except Exception as e:
            print(e)
        finally:
            self.__connection.close()

        return data


    def upload_df(self, df, pk_list, table):
        """
        upload pd.DataFrame() to database
        """

        copy_df = df.copy()
        
        # NaN 값 처리
        copy_df.fillna("", inplace=True)
        for col in copy_df.columns:
            if copy_df[col].dtypes in ['float64', 'int64']:
                copy_df[col] = copy_df[col].astype(str)    

        # 빈 값 처리
        for col in copy_df.columns:
            copy_df[col] = copy_df[col].apply(lambda x: None if x == "" else str(x))


        cols = ', '.join('`{0}`'.format(c) for c in copy_df.columns)
        strings = ', '.join('%s' for i in copy_df.columns)
        update_values = ', '.join('`{0}`=VALUES(`{0}`)'.format(c) for c in copy_df.drop(columns=pk_list).columns)
        values = list(copy_df.itertuples(index=False, name=None))

        # 삽입 sql 문
        sql = "INSERT INTO `" + self.__scheme + "`.`" + table + "` ({0}) VALUES({1}) ON DUPLICATE KEY UPDATE {2};".format(cols, strings, update_values)

        if len(values) == 1:
            values = values[0]
            option = 'one'
        else:
            option = 'many'

        try:
            with self.__connection.cursor() as cursor:
                if option == 'one':
                    cursor.execute(sql, values)
                elif option == 'many':
                    cursor.executemany(sql, values)

                self.__connection.commit()

            return True

        except Exception as e:
            print(e)
            return False

        finally:
            self.__connection.close()


    
    def update_db(self, sql, values, option='one'):
        """
        update mysql database using 'sql' command
        """
        try:
            with self.__connection.cursor() as cursor:
                if option == 'one':
                    cursor.execute(sql, values)
                elif option == 'many':
                    cursor.executemany(sql, values)

                self.__connection.commit()

        except Exception as e:
            print(e)

        finally:
            self.__connection.close()
