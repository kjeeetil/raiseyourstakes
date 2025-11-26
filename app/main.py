from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db, init_db

app = FastAPI(title="Raise Your Stakes", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=FileResponse)
def serve_index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/positions", response_model=List[schemas.PositionSummary])
def list_positions(db: Session = Depends(get_db)) -> List[schemas.PositionSummary]:
    vote_counts = (
        select(
            models.Vote.position_id,
            func.count(models.Vote.id).label("vote_count"),
            func.coalesce(func.sum(models.Vote.stake), 0).label("total_stake"),
            func.group_concat(
                func.coalesce(models.Vote.voter_name, "Anon"), "|"
            ).label("backer_names"),
        )
        .group_by(models.Vote.position_id)
        .subquery()
    )

    query = (
        select(
            models.Position.id,
            models.Position.title,
            models.Position.description,
            models.Position.created_at,
            func.coalesce(vote_counts.c.vote_count, 0).label("vote_count"),
            func.coalesce(vote_counts.c.total_stake, 0).label("total_stake"),
            vote_counts.c.backer_names,
        )
        .outerjoin(vote_counts, models.Position.id == vote_counts.c.position_id)
        .order_by(func.coalesce(vote_counts.c.total_stake, 0).desc())
    )

    results = db.execute(query).all()
    summaries = [
        schemas.PositionSummary(
            id=row.id,
            title=row.title,
            description=row.description,
            created_at=row.created_at,
            vote_count=row.vote_count or 0,
            total_stake=float(row.total_stake or 0),
            backers=(row.backer_names.split("|") if row.backer_names else []),
        )
        for row in results
    ]
    return summaries


@app.post("/positions", response_model=schemas.PositionSummary, status_code=201)
def create_position(
    position: schemas.PositionCreate, db: Session = Depends(get_db)
) -> schemas.PositionSummary:
    db_position = models.Position(
        title=position.title, description=position.description
    )
    db.add(db_position)
    db.commit()
    db.refresh(db_position)

    summary = schemas.PositionSummary(
        id=db_position.id,
        title=db_position.title,
        description=db_position.description,
        created_at=db_position.created_at,
        vote_count=0,
        total_stake=0.0,
        backers=[],
    )
    return summary


@app.post("/positions/{position_id}/votes", response_model=schemas.PositionSummary)
def cast_vote(
    position_id: int, vote: schemas.VoteCreate, db: Session = Depends(get_db)
) -> schemas.PositionSummary:
    position = db.get(models.Position, position_id)
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")

    db_vote = models.Vote(
        position_id=position.id, stake=vote.stake, voter_name=vote.voter_name
    )
    db.add(db_vote)
    db.commit()

    return _position_summary(position.id, db)


@app.get("/positions/{position_id}", response_model=schemas.PositionSummary)
def get_position(position_id: int, db: Session = Depends(get_db)) -> schemas.PositionSummary:
    position = db.get(models.Position, position_id)
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return _position_summary(position.id, db)


def _position_summary(position_id: int, db: Session) -> schemas.PositionSummary:
    vote_counts = (
        select(
            func.count(models.Vote.id).label("vote_count"),
            func.coalesce(func.sum(models.Vote.stake), 0).label("total_stake"),
            func.group_concat(
                func.coalesce(models.Vote.voter_name, "Anon"), "|"
            ).label("backer_names"),
        )
        .where(models.Vote.position_id == position_id)
    )
    vote_stats = db.execute(vote_counts).first()
    position = db.get(models.Position, position_id)
    return schemas.PositionSummary(
        id=position.id,
        title=position.title,
        description=position.description,
        created_at=position.created_at,
        vote_count=vote_stats.vote_count or 0,
        total_stake=float(vote_stats.total_stake or 0),
        backers=(vote_stats.backer_names.split("|") if vote_stats.backer_names else []),
    )
