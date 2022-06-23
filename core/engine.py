import math
import time
from datetime import datetime
from threading import Thread, Timer

from .db import DataBase
from .logger import Logger
from .checker import Checker


class Engine:
    def __init__(self, data_ip_path, logger_path):
        self.logger = Logger(logger_path)
        self.db = DataBase(data_ip_path, self.logger)
        self.checker = Checker(self.logger)
        self.spiders = {}
        self.threadList = []

        self.auto_run_spider_timesleep = 30
        self.auto_check_proxy_timesleep = 60

    def check_proxy_from_spider_part(self, proxy_list, part, name):
        self.logger.log('{}_part{}开始运行.'.format(name,part))
        n_new = 0
        n_exist = 0
        time1 = time.time()
        for proxy in proxy_list:
            type = proxy.get('type', '')
            host = proxy.get('host', '')
            port = proxy.get('port', '')
            address = proxy.get('address', '')
            r = self.checker.check(type, host, port)
            if r:
                anonymity = r['anonymity']
                resptime = r.get('resptime', '0')
                if self.db.is_exist_proxy(type, host, port):
                    time_now = datetime.strftime(datetime.now(), "%m-%d %H:%M:%S")
                    info = self.db.get_info(type, host, port)
                    id = info['id']
                    verify = info['verify']
                    self.db.update_by_id(anonymity, time_now, resptime, 0, verify, id)
                    n_exist += 1
                else:
                    self.db.insert(type, host, port, r['anonymity'], address,
                                   datetime.strftime(datetime.now(), "%m-%d %H:%M:%S"), resptime)
                    n_new += 1
        if self.logger is not None:
            self.logger.log('{}_part{}获取到{}个新有效代理,已存在{}个,'
                            '共筛选{}个.用时:{:.2f}秒'.format(name, part, n_new, n_exist, len(proxy_list),
                                                       time.time() - time1))

    def spider_proxy(self, name, spider):
        self.logger.log('{} start run.'.format(name))
        proxys = spider.get_proxys()
        part = math.ceil(len(proxys) / 50)
        td_list = []
        for i in range(part):
            proxy_list = proxys[50 * i:50 * (i + 1)]
            t = Thread(target=self.check_proxy_from_spider_part, args=(proxy_list, i, name))
            td_list.append(t)
            t.start()
        for ti in td_list:
            ti.join()
        if self.logger is not None:
            self.logger.log('{}完成任务.'.format(name))

    def get_proxy(self, type: str = None, anonymity: str = None, mode: str = 'txt'):
        proxy = self.db.get_one(type, anonymity, mode=mode)
        return proxy

    def add_spider(self, name, spider):
        if name not in self.spiders:
            self.spiders[name] = spider

    def set_spider(self):
        from spiders import Spider1, Spider2, Spider3
        self.add_spider(Spider1.__name__, Spider1())
        self.add_spider(Spider2.__name__, Spider2())
        self.add_spider(Spider3.__name__, Spider3())

    def run_spider(self):
        for name, spider in self.spiders.items():
            t = Thread(target=self.spider_proxy, args=(name, spider))
            self.threadList.append(t)
            t.start()
        for ti in self.threadList:
            ti.join()

    def check_db_proxy_part(self, proxy_list, part):
        if self.logger is not None:
            self.logger.log('开始检查db_part{}.'.format(part))
        n = 0
        time1 = time.time()
        for proxy in proxy_list:
            id = proxy['id']
            type = proxy['type']
            host = proxy['host']
            port = proxy['port']
            dele = proxy['dele']
            verify = proxy['verify']
            r = self.checker.check(type, host, port)
            if not r:
                self.db.delete_by_id(id)
                n += 1
            else:
                time_now = datetime.strftime(datetime.now(), "%m-%d %H:%M:%S")
                self.db.update_by_id(r['anonymity'], time_now, r['resptime'], 0, verify, id)
        if self.logger is not None:
            self.logger.log('检查db_part{}完成:有效{}个,失效{}个,共检查{}个,用时{:.2f}秒'
                            ''.format(part, len(proxy_list) - n, n, len(proxy_list), time.time() - time1))

    def check_db(self):
        if self.logger is not None:
            self.logger.log("开始检查数据库中的代理是否有效")
        results = self.db.get_all(dele=15,resptime=9.99)
        part = math.ceil(len(results) / 50)
        td_list = []
        for i in range(part):
            proxy_list = results[50 * i:50 * (i + 1)]
            t = Thread(target=self.check_db_proxy_part, args=(proxy_list, i))
            td_list.append(t)
            t.start()
        for ti in td_list:
            ti.join()
        if self.logger is not None:
            self.logger.log('数据库中的数据检测完毕！')

    def check_all(self):
        results = self.db.get_all(dele=16,resptime=9.99)
        if self.logger is not None:
            self.logger.log("开始检查所有的数据，共{}条".format(len(results)))
        avg = math.ceil(len(results) / 10)
        td_list = []
        for i in range(10):
            proxy_list = results[avg * i:avg * (i + 1)]
            t = Thread(target=self.check_db_proxy_part, args=(proxy_list, i))
            td_list.append(t)
            t.start()
        for ti in td_list:
            ti.join()
        if self.logger is not None:
            self.logger.log('所有的数据检测完毕！')

    def auto_check(self):
        self.check_db()
        t = Timer(self.auto_check_proxy_timesleep, self.auto_check)
        t.setName('auto_check')
        t.start()

    def auto_run_spider(self):
        self.run_spider()
        t = Timer(self.auto_run_spider_timesleep, self.auto_run_spider)
        t.setName('auto_run_spider')
        t.start()

    def run(self):
        self.set_spider()
        if len(self.spiders) < 1:
            if self.logger is not None:
                self.logger.log("当前没有设置爬虫，请先设置爬虫.!")
            # raise AttributeError("当前没有设置爬虫，请先设置爬虫.")

        thread1 = Thread(target=self.auto_check, name='auto check')
        thread1.start()
        thread2 = Thread(target=self.auto_run_spider(), name='auto_run')
        thread2.start()
        thread1.join()
        thread2.join()
