import logging
import abc
import six
import types
from app.src.data.database.db import eatAllDb


class AbsTable(metaclass=abc.ABCMeta):
    """
    用于实现对表的操作类
    """

    def __init__(self, table_name=None):
        self.table_name = table_name

    def _get_table(self):
        """
        返回表操作实例
        :return:
        """
        if self.table_name:
            return eatAllDb[self.table_name]
        else:
            logging.debug("table_name is None")

    def find_one(self, filter_op=None, *args, **kwargs):
        """
        查找一条数据
        :param filter_op:
        :param args:
        :param kwargs:
        :return:
        """
        table = self._get_table()
        if table:
            return table.find_one(filter_op, *args, **kwargs)
        else:
            logging.debug("The table is None")

    def find(self, *args, **kwargs):
        """
        查找数据
        :param args:
        :param kwargs:
        :return:
        """
        table = self._get_table()
        if table:
            return table.find(*args, **kwargs)
        else:
            logging.debug("The table is None")

    def insert_one(self, doc_or_docs, manipulate=True,
                   check_keys=True, continue_on_error=False, **kwargs):
        """
        插入一条数据
        :param doc_or_docs:
        :param manipulate:
        :param check_keys:
        :param continue_on_error:
        :param kwargs:
        :return:
        """
        table = self._get_table()
        if table:
            return table.insert_one(doc_or_docs, manipulate, check_keys, continue_on_error, kwargs)
        else:
            logging.debug("The table is None")

    def insert_many(self, documents, ordered=True,
                    bypass_document_validation=False, session=None):
        """
        插入多条数据
        :param documents:
        :param ordered:
        :param bypass_document_validation:
        :param session:
        :return:
        """
        table = self._get_table()
        if table:
            return table.insert_many(documents, ordered, bypass_document_validation, session)
        else:
            logging.debug("The table is None")

    def delete_one(self, filter_op, collation=None, session=None):
        """
        删除一条数据
        :param filter_op:
        :param collation:
        :param session:
        :return:
        """
        table = self._get_table()
        if table:
            return table.delete_one(filter_op, collation, session)
        else:
            logging.debug("The table is None")

    def delete_many(self, filter_op, collation=None, session=None):
        """
        删除多条数据
        :param filter_op:
        :param collation:
        :param session:
        :return:
        """
        table = self._get_table()
        if table:
            return table.delete_many(filter_op, collation, session)
        else:
            logging.debug("The table is None")

    def update_one(self, filter_op, update, upsert=False,
                   bypass_document_validation=False,
                   collation=None, array_filters=None, session=None):
        """
        更新一条数据
        :param filter_op:
        :param update:
        :param upsert:
        :param bypass_document_validation:
        :param collation:
        :param array_filters:
        :param session:
        :return:
        """
        table = self._get_table()
        if table:
            return table.update_one(filter_op, update, upsert,
                                    bypass_document_validation, collation, array_filters, session)
        else:
            logging.debug("The table is None")

    def update_many(self, filter_op, update, upsert=False, array_filters=None,
                    bypass_document_validation=False, collation=None,
                    session=None):
        """
        更新多条数据
        :param filter_op:
        :param update:
        :param upsert:
        :param array_filters:
        :param bypass_document_validation:
        :param collation:
        :param session:
        :return:
        """
        table = self._get_table()
        if table:
            return table.update_many(filter_op, update, upsert,
                                     array_filters, bypass_document_validation, collation, session)
        else:
            logging.debug("The table is None")

    def find_and_sort(self, *args, **kwargs):
        """
        查找并进行排序
        :param args:
        :param kwargs:
        :return:
        """
        result = self.find(*args, **kwargs)
        if result:
            return result.sort(kwargs.get("key_or_list"), kwargs.get("direction"))

    def drop(self):
        """
        删除该表
        :return:
        """
        table = self._get_table()
        if table:
            return table.drop()
        else:
            logging.debug("The table is None")


class TableFields(object):
    """
    用于表Field自动生产的包装器
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, cls):
        var_dirt = self.kwargs
        if isinstance(cls, six.class_types):
            init = cls.__init__
            if var_dirt:
                # 创建表列名以及列类型
                for field in var_dirt:
                    setattr(cls, "%s_name" % field, "%s" % field)
                    setattr(cls, "%s_type" % field, var_dirt.get(field))

            def create_table(self, *args):
                """
                创建表方法
                :param args: 数组参数
                :return:
                """
                table = dict()
                if var_dirt and len(args) == len(var_dirt):
                    index = 0
                    for var in var_dirt:
                        table[var] = args[index]
                return table

            cls.create_table = types.MethodType(create_table, cls)

            def wrapper(*args, **kwargs):
                """
                用于替代的构造函数
                :param args: 数组参数
                :param kwargs: 字典参数
                """
                init(*args, **kwargs)
            cls.__init__ = wrapper
            wrapper.__name__ = '__init__'
            wrapper.deprecated_original = init
        return cls
