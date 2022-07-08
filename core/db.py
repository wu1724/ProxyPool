import sqlite3
from datetime import datetime


class DataBase:
    _path = None

    def __init__(self, path, logger=None):
        self._path = path
        self.logger = logger
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self._path,check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_ip(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                host TEXT NOT NULL,
                port TEXT NOT NULL,
                anonymity TEXT NOT NULL,
                address TEXT,
                checktime TEXT,
                resptime TEXT,
                addtime TEXT,
                dele INT,
                verify INT
            )
        ''')
        cursor.close()
        conn.close()
        if self.logger is not None:
            self.logger.log('数据库初始化成功！')

    def get_conn(self):
        conn = sqlite3.connect(self._path,check_same_thread=False)
        return conn

    def insert(self, type, host, port, anonymity, address='', checktime='', resptime='0',dele=0,verify=1):
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = 'INSERT INTO data_ip (type, host, port, anonymity, address, checktime, resptime, addtime, dele, verify)' \
              ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
        try:
            addtime = datetime.strftime(datetime.now(), "%m-%d %H:%M:%S")
            cursor.execute(sql, (type, host, port, anonymity, address, checktime,resptime,addtime,dele,verify))
            conn.commit()
            if self.logger is not None:
                # pass
                self.logger.debug('添加新代理. {}://{}:{}'.format(type, host, port))
        except Exception as e:
            conn.rollback()
            if self.logger is not None:
                pass
                # self.logger.log('Insert failed! {}'.format(e))
        finally:
            self._close(conn, cursor)
        return True

    def _close(self, conn, cursor):
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    def is_exist_proxy(self, type, host, port):
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = "select * from data_ip where (type='{}' and host='{}' and port='{}');".format(type, host, port)
        results = []
        try:
            results = cursor.execute(sql).fetchall()
            if len(results) > 0:
                results = [{'id': r[0], 'type': r[1], 'host': r[2],
                        'port': r[3], 'anonymity': r[4], 'address': r[5], 'dele':r[9]} for r in results]
                if results[0]['dele'] != 0:
                    sql = "UPDATE data_ip SET dele=0 WHERE id={}".format(results[0]['id'])
                    cursor.execute(sql)
                    conn.commit()
        except Exception as e:
            if self.logger is not None:
                self.logger.log('Select failed in is_exist_proxy! {}'.format(e))
        finally:
            self._close(conn, cursor)
        if len(results) > 0:
            # self.logger.debug('{}:{}已存在'.format(results[0]['host'],results[0]['port']))
            return True
        else:
            return False

    def is_exist(self, type, host, port):
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = "select * from data_ip where (type='{}' and host='{}' and port='{}');".format(type, host, port)
        results = []
        try:
            results = cursor.execute(sql).fetchall()
            if len(results) > 0:
                results = [{'id': r[0], 'type': r[1], 'host': r[2],
                            'port': r[3], 'anonymity': r[4], 'address': r[5], 'dele': r[9]} for r in results]
        except Exception as e:
            if self.logger is not None:
                self.logger.log('Select failed in is_exist_proxy! {}'.format(e))
        finally:
            self._close(conn, cursor)
        if len(results) > 0:
            return True
        else:
            return False

    def get_one(self, type:str = None, anonymity:str = None,resptime='1.5',dele=0,verify=5,mode:str = 'txt'):
        conn = self.get_conn()
        cursor = conn.cursor()
        if type is None and anonymity is None:
            sql = "select * from data_ip where resptime<={} and dele<={} and verify>={} " \
                  "order by random() limit 1;".format(resptime,dele,verify)
        else:
            if type is not None and anonymity is not None:
                sql = "select * from data_ip where (type='{}' and anonymity='{}') order by random() limit 1;".format(type, anonymity)
            elif type is not None:
                sql = "select * from data_ip where type='{}' order by random() limit 1;".format(type)
            else:
                sql = "select * from data_ip where anonymity='{}' order by random() limit 1;".format(anonymity)

        results = []
        try:
            results = cursor.execute(sql).fetchall()
            if len(results)>0:
                results = [{'id' : r[0], 'type' : r[1], 'host':r[2] , 'port': r[3],
                            'anonymity':r[4], 'address' : r[5], 'checktime': r[6],
                            'resptime': r[7], 'addtime': r[8]} for r in results]
        except Exception as e:
            if self.logger is not None:
                self.logger.warning('Select failed! {}'.format(e))
        finally:
            self._close(conn, cursor)
        if mode == 'txt':
            return '{}:{}'.format(results[0]['host'],results[0]['port'])
        return results

    def get_all(self,dele=15,verify=1,resptime=10):
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = 'SELECT * FROM data_ip WHERE dele<={} and verify>={} and resptime<={};'.format(dele,verify,resptime)
        # if mode == 0:
        #     sql = 'SELECT * FROM data_ip WHERE dele=0 and verify>10 and resptime<2;'
        # if mode == 1:
        #     sql = 'SELECT * FROM data_ip WHERE dele<15;'
        results = []
        try:
            results = cursor.execute(sql).fetchall()
            if len(results)>0:
                results = [{'id': r[0], 'type': r[1], 'host':r[2], 'port': r[3],
                            'anonymity':r[4], 'address': r[5], 'checktime': r[6],
                            'resptime': r[7], 'addtime': r[8], 'dele': r[9], 'verify': r[10]} for r in results]
        except Exception as e:
            if self.logger is not None:
                self.logger.warning('Select failed! {}'.format(e))
        finally:
            self._close(conn, cursor)
        return results

    def delete_by_id(self, id):
        '''
        根据dele的值来判断是否删除：
        dele < 3: dele+1
        dele >= 3 and verify < 30: 删除
        dele < 10 and verify >= 30: dele+1
        dele >= 10 and verify >= 30: 删除
        :param id:
        :return:
        '''
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = "SELECT * FROM data_ip WHERE id={}".format(id)
        sql2 = "DELETE FROM data_ip WHERE id={}".format(id)
        try:
            results = cursor.execute(sql).fetchall()
            if len(results)>0:
                if results[0][9] <= 15:
                    time_now = datetime.strftime(datetime.now(), "%m-%d %H:%M:%S")
                    sql3 = "UPDATE data_ip SET checktime='{}',dele={} WHERE id={}".format(time_now,results[0][9]+1,id)
                    cursor.execute(sql3)
                    conn.commit()
                # else:
                #     if results[0][10] >= 30 and results[0][9] < 15:
                #         time_now = datetime.strftime(datetime.now(), "%m-%d %H:%M:%S")
                #         sql3 = "UPDATE data_ip SET checktime='{}',dele={} WHERE id={}".format(time_now,
                #                                                                               results[0][9] + 1, id)
                #         cursor.execute(sql3)
                #         conn.commit()
                #     else:
                #         cursor.execute(sql2)
                #         conn.commit()
                #         if self.logger is not None:
                #             self.logger.debug('Delete invalid proxy. The id is {}.'.format(id))
        except Exception as e:
            conn.rollback()
            if self.logger is not None:
                self.logger.warning('Delete failed! {}'.format(e))
        finally:
            self._close(conn, cursor)
        return True

    def update_by_id(self, anonymity:str, checktime:str, resptime:str, dele:int, verify:int, id:int):
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = "UPDATE data_ip SET anonymity='{}',checktime='{}'," \
              "resptime='{}',dele={},verify={} WHERE id={}".format(anonymity, checktime, resptime,dele,verify+1,id)
        try:
            cursor.execute(sql)
            conn.commit()
            if self.logger is not None:
                # self.logger.debug('Update proxy id:{} Anonymity:{} verify:{}'.format(id, anonymity,verify+1))
                pass
        except Exception as e:
            conn.rollback()
            if self.logger is not None:
                self.logger.warning('Update failed! {}'.format(e))
        finally:
            self._close(conn, cursor)
        return True

    def get_info(self,type,host,port):
        conn = self.get_conn()
        cursor = conn.cursor()
        sql = "SELECT * FROM data_ip WHERE (type='{}' and host='{}' and port='{}');".format(type,host,port)
        results = []
        try:
            results = cursor.execute(sql).fetchall()
            if len(results) > 0:
                results = [{'id': r[0], 'type': r[1], 'host': r[2], 'port': r[3],
                            'anonymity': r[4], 'address': r[5], 'checktime': r[6],
                            'resptime': r[7], 'addtime': r[8], 'dele': r[9], 'verify': r[10]} for r in results]
        except Exception as e:
            if self.logger is not None:
                self.logger.warning('Select failed in get_info_by_id! {}'.format(e))
        finally:
            self._close(conn, cursor)
        return results[0]



if __name__ == "__main__":
    pass

