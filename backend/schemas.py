"""Pydantic 模型（Schema）：定义 API 的输入/输出数据格式。

区别于 ORM 模型（models.py 描述"数据库表长什么样"），
Schema 描述"API 收发的 JSON 长什么样"，并自动做数据校验。
FastAPI 用它来校验请求体、生成响应，以及自动生成接口文档。
"""

from datetime import datetime

from pydantic import BaseModel


class ScoreBase(BaseModel):
    """成绩的公共字段（创建和读取都用得到）。"""

    percent: str
    points: str
    time: str
    percent_possible: str
    division: str
    shooter_class: str
    power_factor: str
    hits_a: int = 0
    hits_c: int = 0
    hits_d: int = 0
    misses_m: int = 0
    nopenaltymisses_npm: int = 0
    no_shoots: int = 0
    procedurals: int = 0
    additional_penalties_apen: int = 0


class ScoreCreate(ScoreBase):
    """新增成绩时的请求体（客户端 POST 上来的数据）。"""


class ScoreRead(ScoreBase):
    """返回给客户端的成绩（比创建多了 id 和 created_at）。"""

    id: int
    created_at: datetime

    # 允许从 ORM 对象（models.Score 实例）直接转换成该 Schema
    model_config = {"from_attributes": True}


class ClubBase(BaseModel):
    """俱乐部的公共字段（创建和读取都用得到）。"""

    club_name: str
    club_url: str

class ClubCreate(ClubBase):
    """新增俱乐部时的请求体（客户端 POST 上来的数据）。"""

    club_name: str
    club_url: str

class ClubRead(ClubBase):
    """返回给客户端的俱乐部（比创建多了 id 和 created_at）。"""

    id: int

    # 允许从 ORM 对象（models.Club 实例）直接转换成该 Schema
    model_config = {"from_attributes": True}

class ClubUpdate(ClubBase):
    """更新俱乐部时的请求体（客户端 PUT 上来的数据）。"""

    club_name: str
    club_url: str

class ClubDelete(BaseModel):
    """删除俱乐部时的请求体（客户端 DELETE 上来的数据）。"""

    id: int