"""
RQ Worker runner

Run with: python -m src.workers.run_worker
"""
from redis import Redis
from rq import SimpleWorker, Queue

from ..config import settings, logger


def main():
    """Start RQ worker (Windows-compatible)"""
    logger.info("Starting RQ worker...")

    # Connect to Redis
    redis_conn = Redis.from_url(settings.redis_url, decode_responses=False)

    # Create worker (SimpleWorker for Windows compatibility - no forking)
    worker = SimpleWorker(['default'], connection=redis_conn)
    logger.info("Worker started and listening to 'default' queue")
    worker.work()


if __name__ == "__main__":
    main()
