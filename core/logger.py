from datetime import datetime


class Logger:
    def __init__(self, path):
        self.path = path

    def log(self, info):
        with open(self.path, 'a+') as logs:
            info = '{}: {}\n'.format(datetime.strftime(datetime.now(), "%Y-%m-%d-%H:%M:%S"), info)
            print(info)
            logs.write(info)

    def debug(self, info):
        with open(self.path, 'a+') as logs:
            info = '{}: {}\n'.format(datetime.strftime(datetime.now(), "%Y-%m-%d-%H:%M:%S"), info)
            logs.write(info)

    def warning(self, info):
        with open(self.path, 'a+') as logs:
            info = '{}: {}\n'.format(datetime.strftime(datetime.now(), "%Y-%m-%d-%H:%M:%S"), info)
            print(info)
            logs.write(info)


if __name__ == '__main__':
    logger = Logger('test.log')
    logger.log('hello')
