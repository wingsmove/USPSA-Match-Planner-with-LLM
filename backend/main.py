"""FastAPI 应用入口：定义 HTTP 接口（API）。

运行方式（在 backend 目录下）：
    uvicorn main:app --reload
启动后：
    - 接口文档（自动生成）：http://127.0.0.1:8000/docs
    - 健康检查：http://127.0.0.1:8000/
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from analysis import analyze_db_scores, plan_matches
from database import Base, engine, get_db
from import_export import export_db_to_json, import_json_to_db

# 根据 models 里的定义，在数据库中创建还不存在的表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="USPSA Score API")

# CORS：允许前端（Vite 默认跑在 5173 端口）跨域访问本后端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    """健康检查接口，用于确认服务是否在运行。"""
    return {"status": "ok"}


@app.get("/scores", response_model=list[schemas.ScoreRead])
def list_scores(db: Session = Depends(get_db)):
    """查询所有成绩（按创建时间倒序）。"""
    return db.query(models.Score).order_by(models.Score.created_at.desc()).all()


@app.post("/scores", response_model=schemas.ScoreRead, status_code=201)
def create_score(score: schemas.ScoreCreate, db: Session = Depends(get_db)):
    """新增一条成绩。"""
    db_score = models.Score(**score.model_dump())  # Schema -> ORM 对象
    db.add(db_score)     # 加入会话
    db.commit()          # 提交事务，真正写入数据库
    db.refresh(db_score)  # 刷新以拿到数据库生成的 id 和 created_at
    return db_score

@app.delete("/scores/{score_id}", status_code=204)
def delete_score(score_id: int, db: Session = Depends(get_db)):
    """删除一条成绩（成功返回 204 No Content，无响应体）。"""
    db_score = db.query(models.Score).filter(models.Score.id == score_id).first()
    if not db_score:
        raise HTTPException(status_code=404, detail="成绩不存在")
    db.delete(db_score)
    db.commit()
    # 204 表示"成功但无内容"，因此不返回 body


@app.post("/scores/import")
def import_scores(db: Session = Depends(get_db)):
    """一键导入：把 Past_Scores/scores_db.json 里的成绩写入数据库。"""
    try:
        count = import_json_to_db(db)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"imported": count}


@app.get("/scores/export")
def export_scores(db: Session = Depends(get_db)):
    """一键导出：把数据库里所有成绩导出为带时间戳的 JSON 文件。"""
    count, path = export_db_to_json(db)
    return {"exported": count, "file": path}


@app.post("/analyze")
def analyze(db: Session = Depends(get_db)):
    """让 AI 教练分析数据库里的成绩，返回 markdown 报告。"""
    if not db.query(models.Score).first():
        raise HTTPException(status_code=400, detail="数据库暂无成绩，无法分析")
    report = analyze_db_scores(db)
    return {"report": report}

@app.get("/clubs", response_model=list[schemas.ClubRead])
def list_clubs(db: Session = Depends(get_db)):
    """查询所有俱乐部（按创建时间倒序）。"""
    return db.query(models.Club).order_by(models.Club.id.desc()).all()

@app.post("/clubs", response_model=schemas.ClubRead, status_code=201)
def create_club(club: schemas.ClubCreate, db: Session = Depends(get_db)):
    """新增一条俱乐部。"""
    db_club = models.Club(**club.model_dump())  # Schema -> ORM 对象
    db.add(db_club)     # 加入会话
    db.commit()          # 提交事务，真正写入数据库
    db.refresh(db_club)  # 刷新以拿到数据库生成的 id 和 created_at
    return db_club

@app.delete("/clubs/{club_id}", status_code=204)
def delete_club(club_id: int, db: Session = Depends(get_db)):
    """删除一条俱乐部（成功返回 204 No Content，无响应体）。"""
    db_club = db.query(models.Club).filter(models.Club.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=404, detail="俱乐部不存在")
    db.delete(db_club)
    db.commit()
    # 204 表示"成功但无内容"，因此不返回 body

@app.post("/plan")
def plan(db: Session = Depends(get_db)):
    """让 AI 教练根据俱乐部规划比赛。"""
    if not db.query(models.Club).first():
        raise HTTPException(status_code=400, detail="数据库暂无俱乐部，无法规划")
    plan = plan_matches(db)
    return {"plan": plan}