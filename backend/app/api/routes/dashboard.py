"""Dashboard analytics routes."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.middleware.request_id import get_request_id
from app.api.schemas.common import wrap_data
from app.application.dashboard_service import DashboardService
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(request: Request, session: Session = Depends(get_db)):
    data = DashboardService(session).get_summary()
    return wrap_data(data, get_request_id(request))


@router.get("/trends")
def dashboard_trends(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    session: Session = Depends(get_db),
):
    data = DashboardService(session).get_trends(days)
    return wrap_data(data, get_request_id(request))
