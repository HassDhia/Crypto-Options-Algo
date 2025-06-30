from prometheus_client import Counter


class PrometheusMetrics:
    """Metrics collector for the ingestor service"""

    def __init__(self):
        self.ticks_emitted = Counter(
            'ingestor_ticks_emitted_total',
            'Total number of option snapshots '
            'emitted to Kafka',
            ['asset']
        )
        self.incomplete_snapshots = Counter(
            'ingestor_snapshot_incomplete_total',
            'Total number of incomplete '
            'snapshots dropped',
            ['asset']
        )

    def incr(
        self,
        metric_name: str,
        value: int = 1,
        asset: str = None
    ) -> None:
        """Increment a metric counter"""
        if metric_name == 'ingestor_ticks_emitted_total':
            self.ticks_emitted.labels(
                asset=asset or 'all'
            ).inc(value)
        elif metric_name == 'ingestor_snapshot_incomplete_total':
            self.incomplete_snapshots.labels(
                asset=asset or 'all'
            ).inc(value)
