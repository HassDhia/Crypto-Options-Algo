import json
import logging
import os
import time
from confluent_kafka import Consumer
import psycopg2
import numpy as np
from scipy import stats

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Database configuration

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "options_trading")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")


# Kafka configuration

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
SCOUTED_OPTIONS_TOPIC = "scouted_options"
EXECUTED_TRADES_TOPIC = "executed_trades"


# Connect to PostgreSQL
def create_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# Create tables if not exists
def initialize_database():
    conn = create_db_connection()
    cur = conn.cursor()

    # Create scouted options table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scouted_options (
        id SERIAL PRIMARY KEY,
        instrument VARCHAR(50) NOT NULL,
        timestamp BIGINT NOT NULL,
        score FLOAT NOT NULL,
        bid_ask_spread FLOAT NOT NULL,
        mark_iv FLOAT NOT NULL,
        delta FLOAT NOT NULL,
        underlying_price FLOAT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create executed trades table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS executed_trades (
        id SERIAL PRIMARY KEY,
        instrument VARCHAR(50) NOT NULL,
        trade_type VARCHAR(10) NOT NULL,
        quantity INTEGER NOT NULL,
        price FLOAT NOT NULL,
        timestamp BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create performance metrics table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS performance_metrics (
        id SERIAL PRIMARY KEY,
        instrument VARCHAR(50) NOT NULL,
        entry_timestamp BIGINT NOT NULL,
        exit_timestamp BIGINT,
        entry_price FLOAT NOT NULL,
        exit_price FLOAT,
        pnl FLOAT,
        duration_hours FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    cur.close()
    conn.close()


def calculate_performance_metrics():
    """Calculate performance metrics for completed trades"""
    conn = create_db_connection()
    cur = conn.cursor()

    # Get completed trades (with both entry and exit)
    cur.execute("""
    SELECT e1.instrument, e1.timestamp AS entry_time,
           e2.timestamp AS exit_time, e1.price AS entry_price,
           e2.price AS exit_price
    FROM executed_trades e1
    JOIN executed_trades e2 ON e1.instrument = e2.instrument
    WHERE e1.trade_type = 'BUY' AND e2.trade_type = 'SELL'
    AND e1.timestamp < e2.timestamp
    AND NOT EXISTS (
        SELECT 1 FROM performance_metrics pm
        WHERE pm.instrument = e1.instrument
        AND pm.entry_timestamp = e1.timestamp
    );
    """)

    trades = cur.fetchall()

    for trade in trades:
        instrument, entry_time, exit_time, entry_price, exit_price = trade

        # Calculate P&L
        pnl = (exit_price - entry_price) * 100  # 1 contract = 100 options

        # Calculate duration in hours
        duration_hours = (exit_time - entry_time) / 3600

        # Insert into performance metrics
        cur.execute("""
        INSERT INTO performance_metrics (
            instrument, entry_timestamp, exit_timestamp,
            entry_price, exit_price, pnl, duration_hours
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            instrument, entry_time, exit_time,
            entry_price, exit_price, pnl, duration_hours
        ))

    conn.commit()
    cur.close()
    conn.close()


def reinforcement_learning_update():
    """Update RL model based on performance metrics"""
    conn = create_db_connection()
    cur = conn.cursor()

    # Get recent performance data
    cur.execute("""
    SELECT score, pnl, duration_hours
    FROM scouted_options so
    JOIN performance_metrics pm ON so.instrument = pm.instrument
    WHERE pm.created_at > NOW() - INTERVAL '30 days'
    """)

    data = cur.fetchall()

    if not data:
        logger.info("No performance data available for RL update")
        return

    # Prepare data for RL model
    scores = np.array([d[0] for d in data])
    pnls = np.array([d[1] for d in data])

    # Calculate performance metrics
    win_rate = np.mean(pnls > 0)
    avg_pnl = np.mean(pnls)
    sharpe_ratio = avg_pnl / np.std(pnls) if np.std(pnls) > 0 else 0

    # Calculate correlation between scout score and P&L
    score_pnl_corr, _ = stats.pearsonr(scores, pnls)

    logger.info("Reinforcement Learning Update:")
    logger.info(f"  Win Rate: {win_rate:.2%}")
    logger.info(f"  Avg P&L: ${avg_pnl:.2f}")
    logger.info(f"  Sharpe Ratio: {sharpe_ratio:.2f}")
    logger.info(f"  Score-P&L Correlation: {score_pnl_corr:.2f}")

    # TODO: Implement actual RL model update
    # This would typically involve updating model weights
    # based on the correlation between scout scores and actual P&L

    cur.close()
    conn.close()


def main():
    logger.info("Starting options backtester...")
    initialize_database()

    # Kafka consumer configuration
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': 'backtester-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True
    }

    consumer = Consumer(conf)
    consumer.subscribe([SCOUTED_OPTIONS_TOPIC, EXECUTED_TRADES_TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            # Process message
            try:
                data = json.loads(msg.value().decode('utf-8'))
                conn = create_db_connection()
                cur = conn.cursor()

                if msg.topic() == SCOUTED_OPTIONS_TOPIC:
                    # Store scouted option in database
                    cur.execute("""
                    INSERT INTO scouted_options (
                        instrument, timestamp, score,
                        bid_ask_spread, mark_iv, delta, underlying_price
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        data['instrument'],
                        data['timestamp'],
                        data['score'],
                        data['bid_ask_spread'],
                        data['mark_iv'],
                        data['delta'],
                        data['underlying_price']
                    ))
                    logger.info(
                        f"Stored scouted option: {data['instrument']}"
                    )

                elif msg.topic() == EXECUTED_TRADES_TOPIC:
                    # Store executed trade in database
                    cur.execute("""
                    INSERT INTO executed_trades (
                        instrument, trade_type, quantity, price, timestamp
                    ) VALUES (%s, %s, %s, %s, %s)
                    """, (
                        data['instrument'],
                        data['trade_type'],
                        data['quantity'],
                        data['price'],
                        data['timestamp']
                    ))
                    logger.info(
                        f"Stored {data['trade_type']} trade: "
                        f"{data['instrument']}"
                    )

                conn.commit()
                cur.close()
                conn.close()

            except Exception as e:
                logger.error(f"Error processing message: {e}")

            # Periodically run performance calculations and RL updates
            current_time = int(time.time())
            # Run every 5 minutes
            if current_time % 300 == 0:
                calculate_performance_metrics()
                reinforcement_learning_update()
                time.sleep(1)  # Avoid multiple runs in same second

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
