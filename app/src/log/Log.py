import logging
import os


class Log(object):
    """
    重写log,使其有自己的配置
    """

    def __init__(self, name="eat_all_system"):
        self.log_name = name
        self.log = logging.getLogger(self.log_name)
        self.log.setLevel(logging.DEBUG)
        self._config_log_inf()

    def _config_log_inf(self):
        """
        配置全局log信息
        :return:
        """
        log_save_path = os.path.dirname(os.path.abspath(__file__))
        log_file_name = "%s/%s.log" % (log_save_path, self.log_name)
        file_handler = logging.FileHandler(log_file_name, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(filename)s-[line:%(lineno)d]'
                                      '-%(levelname)s-[日志信息]: %(message)s',
                                      datefmt='%a, %d %b %Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        self.log.addHandler(file_handler)
        self.log.addHandler(stream_handler)

    def d(self, message):
        """
        写入debug信息
        :param message:
        :return:
        """
        self.log.debug(message)


def d(message):
    Log().d(message)
