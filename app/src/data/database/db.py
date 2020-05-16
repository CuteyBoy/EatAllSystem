import pymongo

# 数据库名
DATABASE_NAME = 'EatAllDb'
# 初始化数据库客户端
dataClient = pymongo.MongoClient('mongodb://localhost:27017')
# 初始化数据库
eatAllDb = dataClient[DATABASE_NAME]

