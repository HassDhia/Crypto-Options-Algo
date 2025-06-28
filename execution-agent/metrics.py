from prometheus_client import Gauge, start_http_server

# Define metrics
edge_capture = Gauge('edge_capture_pct', 'Realised / theoretical edge (0-1)')
slip_bp = Gauge('fill_slip_bp', 'Absolute slippage in basis points')
cum_pnl = Gauge('cum_pnl_usd', 'Cumulative realised PnL in USD')

def start_metrics_server():
    """Start Prometheus metrics HTTP server on port 8000"""
    start_http_server(8000)
