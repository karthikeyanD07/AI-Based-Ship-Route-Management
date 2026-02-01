"""Metrics endpoint."""
from fastapi import APIRouter
from backend.app.utils.metrics import metrics
from backend.app.utils.monitoring import get_system_metrics
from prometheus_client import generate_latest
from starlette.responses import Response

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def get_prometheus_metrics():
    """Get Prometheus metrics."""
    return Response(content=generate_latest(), media_type="text/plain")


@router.get("/metrics/system")
async def get_system_metrics_endpoint():
    """Get system metrics in JSON format."""
    return get_system_metrics()
