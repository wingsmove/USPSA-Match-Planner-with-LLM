"""数据库连接与会话管理（SQLAlchemy + SQLite）。

SQLAlchemy 是 Python 最常用的 ORM（对象关系映射）：
让你用「Python 类/对象」来操作数据库表，而不用手写 SQL。
这里用 SQLite——一个基于单个文件（app.db）的轻量数据库，零配置，适合入门。
以后换成 PostgreSQL/MySQL 时，通常只需改 DATABASE_URL。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 数据库地址：sqlite 表示使用 SQLite，./app.db 是当前目录下的数据库文件
DATABASE_URL = "sqlite:///./app.db"

# engine：数据库引擎，负责实际的连接。
# check_same_thread=False 是 SQLite 在多线程（FastAPI）下的必要设置。
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal：每次请求会创建一个「会话（Session）」，用来执行增删改查。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base：所有 ORM 模型（数据表）都要继承它。
Base = declarative_base()


def get_db():
    """FastAPI 依赖：为每个请求提供一个数据库会话，用完自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
