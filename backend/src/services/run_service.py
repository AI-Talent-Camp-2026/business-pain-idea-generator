from sqlalchemy.orm import Session
from redis import Redis
from rq import Queue
import uuid

from ..models import Run, Idea
from ..config import settings, logger

# Initialize Redis connection and queue
redis_conn = Redis.from_url(settings.redis_url, decode_responses=False)
queue = Queue(connection=redis_conn, default_timeout=settings.generation_timeout_seconds)


def create_run(db: Session, optional_direction: str = None) -> Run:
    """Create a new run and enqueue generation job"""
    # Create run record
    run = Run(
        id=str(uuid.uuid4()),
        optional_direction=optional_direction,
        status='pending'
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    # Enqueue generation job
    try:
        from ..workers.generation_pipeline import generate_ideas
        job = queue.enqueue(
            generate_ideas,
            run.id,
            job_timeout=settings.generation_timeout_seconds
        )
        logger.info(f"Enqueued generation job {job.id} for run {run.id}")
    except Exception as e:
        logger.error(f"Failed to enqueue job for run {run.id}: {e}")
        run.status = 'failed'
        run.error_message = f"Ошибка постановки задачи: {str(e)}"
        db.commit()

    return run


def get_run_status(db: Session, run_id: str) -> Run:
    """Get run by ID"""
    return db.query(Run).filter(Run.id == run_id).first()


def get_run_ideas(db: Session, run_id: str):
    """Get all ideas for a run"""
    return db.query(Idea).filter(Idea.run_id == run_id).order_by(Idea.order_index).all()
