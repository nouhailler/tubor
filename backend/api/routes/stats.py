"""
Tubor Web — Routes API : statistiques & historique
"""

from fastapi import APIRouter, Query

from core.database import history
from models.schemas import (
    StatsSummaryResponse, DailyStatResponse,
    PlatformStatResponse, FormatStatResponse, HistoryItemResponse,
)

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummaryResponse)
def stats_summary():
    return history.get_summary()


@router.get("/daily", response_model=list[DailyStatResponse])
def stats_daily(days: int = Query(14, ge=1, le=90)):
    return history.get_daily(days)


@router.get("/platforms", response_model=list[PlatformStatResponse])
def stats_platforms():
    return history.get_platforms()


@router.get("/formats", response_model=list[FormatStatResponse])
def stats_formats():
    return history.get_formats()


@router.get("/history", response_model=list[HistoryItemResponse])
def stats_history(
    limit:         int = Query(50,  ge=1,  le=200),
    offset:        int = Query(0,   ge=0),
    status_filter: str = Query(""),
    format_filter: str = Query(""),
):
    return history.get_history(
        limit=limit, offset=offset,
        status_filter=status_filter,
        format_filter=format_filter,
    )
