import pymysql
pymysql.install_as_MySQLdb()
import os
os.environ["queue_env"] = "prod"
