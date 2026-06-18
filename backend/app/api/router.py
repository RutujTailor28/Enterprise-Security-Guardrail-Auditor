"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.routes import dashboard, files, findings, health, reports, rules, scans

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(scans.router)
api_router.include_router(findings.router)
api_router.include_router(files.router)
api_router.include_router(rules.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)
