import pymysql

def get_connection():
    return pymysql.connect(
        host="145.79.213.60",
        user="u127621062_joba",
        password="CaneSetu@3d",
        database="u127621062_jobs",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )