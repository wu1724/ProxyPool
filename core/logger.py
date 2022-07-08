from datetime import datetime


class Logger:
    def __init__(self, path, mode=2):
        self.path = path
        self.mode = mode
        self.modeList = ["DEBUG", "WARN", "INFO", "ERROR", "OFF"]

    def log(self, info, mode=-1):
        if mode == -1:
            mode = self.mode
        with open(self.path, 'a+') as logs:
            info = '{}-{}: {}\n'.format(self.modeList[mode],
                                        datetime.strftime(datetime.now(), "%Y-%m-%d-%H:%M:%S"), info)
            print(info, end="")
            logs.write(info)

    def debug(self, info):
        with open(self.path, 'a+') as logs:
            info = 'debug-{}: {}\n'.format(datetime.strftime(datetime.now(), "%Y-%m-%d-%H:%M:%S"), info)
            logs.write(info)

    def warn(self, info):
        with open(self.path, 'a+') as logs:
            info = 'warning-{}: {}\n'.format(datetime.strftime(datetime.now(), "%Y-%m-%d-%H:%M:%S"), info)
            print(info)
            logs.write(info)


if __name__ == '__main__':
    logger = Logger('test.log')
    logger.log('hello')
