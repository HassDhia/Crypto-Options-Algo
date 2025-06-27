import os
import logging
import json
import redis
import openai
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RLParameterTuner:
    """Agent that uses OpenAI API to tune filter parameters."""
    def __init__(self):
        # Connect to Redis
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv(
                'REDIS_PORT', 6379
            )),
            db=0
        )

        # Set OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            logger.warning(
                "OpenAI API key not set. RL tuner will not function without it."
            )

        # Initialize scheduler
        self.scheduler = BlockingScheduler()

    def get_recent_trade_stats(self):
        """Fetch recent trading performance stats with current parameters."""
        try:
            # Get trade performance stats
            stats_data = self.redis.get("trade_stats:recent")
            stats = json.loads(stats_data) if stats_data else {}

            # Get current filter parameters
            params = self.redis.hgetall("filter_params")
            if params:
                # Convert Redis byte strings to appropriate types
                stats["delta_min"] = float(params.get(b'delta_min', b'0.25'))
                stats["delta_max"] = float(params.get(b'delta_max', b'0.75'))
                stats["min_edge"] = float(params.get(b'min_edge', b'0.0'))
                stats["max_skew"] = float(params.get(b'max_skew', b'10.0'))
                stats["avoid_iv_crush"] = params.get(
                    b'avoid_iv_crush', b'False'
                ).decode('utf-8') == 'True'

            return stats
        except Exception as e:
            logger.error(
                f"Error fetching trade stats and params from Redis: {e}"
            )
            # Fallback to simulated stats with default parameters
            return {
                "trades": 42,
                "wins": 25,
                "losses": 17,
                "win_rate": 0.595,
                "avg_profit": 0.018,
                "avg_edge": 0.062,
                "delta_min": 0.25,
                "delta_max": 0.75,
                "min_edge": 0.0,
                "max_skew": 10.0,
                "avoid_iv_crush": False
            }

    def suggest_new_parameters(self, stats) -> dict:
        """Call OpenAI API to get suggested parameter tweaks."""
        if not openai.api_key:
            logger.warning("Skipping OpenAI call - API key not set")
            return {}

        # Formulate prompt with more context
        prompt = (
            "We have the following recent trading performance:\n"
            f"- Trades: {stats['trades']} "
            f"(Wins: {stats['wins']}, Losses: {stats['losses']})\n"
            f"- Win Rate: {stats['win_rate']*100:.1f}%\n"
            f"- Avg Profit per Trade: {stats['avg_profit']*100:.2f}%\n"
            f"- Current Parameters:\n"
            f"  - Delta Range: "
            f"{stats['delta_min']*100:.1f}%-{stats['delta_max']*100:.1f}%\n"
            f"  - Min Edge: {stats['min_edge']*100:.2f}%\n"
            f"  - Max IV Skew: {stats['max_skew']:.2f}\n"
            f"  - Avoid IV Crush: {stats['avoid_iv_crush']}\n\n"
            "The goal is to improve win rate and profit. Suggest updated parameters "
            "in JSON format with any combination of these keys: "
            "'delta_min', 'delta_max', 'min_edge', "
            "'max_skew', 'avoid_iv_crush'. "
            "Only suggest changes that would improve performance. "
            "Only respond with the JSON object and nothing else."
        )

        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.1
            )
            answer = response.choices[0].message["content"].strip()
            logger.info(f"OpenAI response: {answer}")

            try:
                # Parse JSON response
                params = json.loads(answer)

                # Validate and filter parameters
                valid_params = {}
                for key, value in params.items():
                    if key == "delta_min" and 0 <= value <= 1:
                        valid_params[key] = value
                    elif key == "delta_max" and 0 <= value <= 1:
                        valid_params[key] = value
                    elif key == "min_edge" and value >= 0:
                        valid_params[key] = value
                    elif key == "max_skew" and value > 0:
                        valid_params[key] = value
                    elif key == "avoid_iv_crush" and isinstance(value, bool):
                        valid_params[key] = value

                return valid_params
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON response from OpenAI")
                return {}
            except Exception as e:
                logger.error(f"Error processing OpenAI response: {e}")
                return {}

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return {}

    def update_filter_params(self, new_params: dict):
        """Write updated parameters to Redis."""
        if not new_params:
            return

        try:
            # Update Redis hash
            for key, value in new_params.items():
                self.redis.hset("filter_params", key, value)
            logger.info(f"Updated filter parameters: {new_params}")
        except Exception as e:
            logger.error(f"Failed to update Redis: {e}")

    def tune_parameters(self):
        """Main tuning routine."""
        logger.info("Starting parameter tuning cycle")
        stats = self.get_recent_trade_stats()
        suggestions = self.suggest_new_parameters(stats)
        if suggestions:
            self.update_filter_params(suggestions)
        else:
            logger.info("No parameter updates applied")

    def start(self):
        """Start the periodic tuning scheduler."""
        # Schedule hourly runs
        self.scheduler.add_job(
            self.tune_parameters,
            'interval',
            hours=int(os.getenv("TUNING_INTERVAL_HOURS", 1)),
            next_run_time=datetime.now() + timedelta(seconds=10)
        )
        logger.info("Starting RL Parameter Tuner scheduler")
        self.scheduler.start()


if __name__ == "__main__":
    tuner = RLParameterTuner()
    tuner.start()
