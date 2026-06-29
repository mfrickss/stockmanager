import pymysql

pymysql.install_as_MySQLdb()

# Fake version to bypass Django 5's mysqlclient version check
import MySQLdb
MySQLdb.version_info = (2, 2, 4, 'final', 0)
