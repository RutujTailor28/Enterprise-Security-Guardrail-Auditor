"""Security rules routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.middleware.request_id import get_request_id
from app.api.schemas.common import wrap_data
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.rule_repository import ScanRuleRepository

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("")
def list_rules(request: Request, session: Session = Depends(get_db)):
    rules = ScanRuleRepository(session).list_all()
    data = [
        {
            "id": r.id,
            "name": r.name,
            "severity_default": r.severity_default,
            "description": r.description,
            "enabled": r.enabled,
        }
        for r in rules
    ]
    return wrap_data(data, get_request_id(request))
