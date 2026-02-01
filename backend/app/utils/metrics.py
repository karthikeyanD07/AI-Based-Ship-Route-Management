"""Metrics collection for monitoring."""
import time
import logging
from typing import Dict
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Simple metrics collector (can be replaced with Prometheus)."""
    
    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._timers: Dict[str, list] = defaultdict(list)
        self._gauges: Dict[str, float] = {}
        self._start_time = datetime.utcnow()
    
    def increment(self, metric_name: str, value: int = 1):
        """Increment a counter metric."""
        self._counters[metric_name] += value
    
    def record_timing(self, metric_name: str, duration_ms: float):
        """Record a timing metric."""
        self._timers[metric_name].append(duration_ms)
        # Keep only last 1000 timings
        if len(self._timers[metric_name]) > 1000:
            self._timers[metric_name] = self._timers[metric_name][-1000:]
    
    def set_gauge(self, metric_name: str, value: float):
        """Set a gauge metric."""
        self._gauges[metric_name] = value
    
    def get_metrics(self) -> Dict:
        """Get all metrics."""
        uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()
        
        # Calculate averages for timers
        timer_stats = {}
        for name, timings in self._timers.items():
            if timings:
                timer_stats[name] = {
                    "count": len(timings),
                    "avg_ms": sum(timings) / len(timings),
                    "min_ms": min(timings),
                    "max_ms": max(timings)
                }
        
        return {
            "uptime_seconds": uptime_seconds,
            "counters": dict(self._counters),
            "timers": timer_stats,
            "gauges": dict(self._gauges)
        }


# Global metrics instance
metrics = MetricsCollector()
