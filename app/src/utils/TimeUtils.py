import time


# 五年时间差
DIFF_5_YEAR = 5 * 365 * 24 * 60 * 60
# 年限差，默认是6
DIFF_YEAR_SIZE = 6


class StockTimeUtils:
    """
    用于封装计算股票需要的时间
    """

    @staticmethod
    def get_now_time_str(format_sample="%Y-%m-%d"):
        return time.strftime(format_sample, time.localtime(time.time()))

    @staticmethod
    def is_more_than_5(start_time):
        """
        用于判断公司上市是否满足五年
        :param start_time: 上市时间
        :return: True表示超过，否则表示没有
        """
        if start_time is None:
            start_time = StockTimeUtils.get_now_time_str()
        start_time_second = time.mktime(time.strptime(start_time, "%Y-%m-%d"))
        diff_rate = (time.time() - start_time_second) / DIFF_5_YEAR
        if diff_rate >= 1:
            return True
        else:
            return False

    @staticmethod
    def get_start_time(diff_year=DIFF_YEAR_SIZE):
        """
        获取财报的开始时间，比如2016-12-31
        :param diff_year: 现在举例过去的的年限差，默认是6
        :return:
        """
        now_year = StockTimeUtils.get_now_year()
        return "%s-12-31" % (int(now_year) - diff_year)

    @staticmethod
    def get_now_year():
        return StockTimeUtils.get_now_time_str().split('-')[0]

    @staticmethod
    def get_start_year(diff_year=DIFF_YEAR_SIZE):
        now_year = StockTimeUtils.get_now_year()
        return str(int(now_year) - diff_year)

    @staticmethod
    def sleep(time_second):
        time.sleep(time_second)
