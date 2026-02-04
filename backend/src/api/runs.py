from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..models import get_db
from ..services.run_service import create_run, get_run_status, get_run_ideas
from ..config import settings, logger
import asyncio
import json

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class CreateRunRequest(BaseModel):
    optional_direction: Optional[str] = None


@router.post("/runs")
@limiter.limit(f"{settings.rate_limit_runs_per_hour}/hour")
async def create_new_run(
    request: Request,
    request_data: CreateRunRequest,
    db: Session = Depends(get_db)
):
    """Create a new idea generation run"""
    try:
        run = create_run(db, request_data.optional_direction)
        logger.info(f"Created new run: {run.id}")

        return {
            "run_id": run.id,
            "status": run.status,
            "created_at": run.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating run: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания прогона: {str(e)}")


@router.get("/runs/{run_id}")
async def get_run(run_id: str, db: Session = Depends(get_db)):
    """Get run status and details"""
    run = get_run_status(db, run_id)

    if not run:
        raise HTTPException(status_code=404, detail="Прогон не найден")

    return run.to_dict()


@router.get("/runs/{run_id}/progress")
async def stream_progress(run_id: str, db: Session = Depends(get_db)):
    """
    Server-Sent Events endpoint for real-time progress updates

    Note: For MVP, we use polling fallback. Full SSE can be added later.
    """
    async def event_generator():
        """Generate SSE events with run progress"""
        max_duration = 600  # 10 minutes timeout
        start_time = asyncio.get_event_loop().time()

        while True:
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > max_duration:
                yield f"event: error\ndata: {json.dumps({'error_message': 'Превышено время ожидания'})}\n\n"
                break

            # IMPORTANT: Refresh DB session to get latest data
            db.expire_all()
            run = get_run_status(db, run_id)

            if not run:
                yield f"event: error\ndata: {json.dumps({'error_message': 'Прогон не найден'})}\n\n"
                break

            if run.status == 'completed':
                yield f"event: complete\ndata: {json.dumps(run.to_dict())}\n\n"
                break
            elif run.status == 'failed':
                yield f"event: error\ndata: {json.dumps(run.to_dict())}\n\n"
                break
            else:
                yield f"event: progress\ndata: {json.dumps(run.to_dict())}\n\n"

            await asyncio.sleep(5)  # Poll every 5 seconds

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/runs/{run_id}/logs")
async def stream_logs(run_id: str, db: Session = Depends(get_db)):
    """Stream live logs for a running generation"""
    import time

    async def log_generator():
        """Generate simulated logs based on run status"""
        max_duration = 600
        start_time = time.time()

        # Initial logs
        yield f"data: {json.dumps({'timestamp': time.time(), 'message': f'Starting generation for run {run_id}...'})}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'timestamp': time.time(), 'message': 'Connecting to OpenRouter API...'})}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'timestamp': time.time(), 'message': 'Model: anthropic/claude-3.5-sonnet'})}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'timestamp': time.time(), 'message': 'Temperature: 0.7, Max tokens: 8000'})}\n\n"
        await asyncio.sleep(1)

        log_messages = [
            "Analyzing pain signals from public sources...",
            "Searching for user complaints and feedback...",
            "Identifying recurring pain patterns...",
            "Evaluating market segments...",
            "Generating business ideas...",
            "Brainstorming creative solutions...",
            "Searching for analogues and competitors...",
            "Analyzing successful implementations...",
            "Creating validation evidence...",
            "Drafting 7-day action plans...",
            "Drafting 30-day roadmaps...",
            "Finalizing idea descriptions...",
        ]

        log_index = 0

        while True:
            current_time = time.time()
            if current_time - start_time > max_duration:
                yield f"data: {json.dumps({'timestamp': time.time(), 'message': 'ERROR: Timeout exceeded', 'type': 'error'})}\n\n"
                break

            # IMPORTANT: Refresh DB session to get latest data
            db.expire_all()
            run = get_run_status(db, run_id)

            if not run:
                yield f"data: {json.dumps({'timestamp': time.time(), 'message': 'ERROR: Run not found', 'type': 'error'})}\n\n"
                break

            # Log current status for debugging
            yield f"data: {json.dumps({'timestamp': time.time(), 'message': f'[DEBUG] Status: {run.status}, Ideas: {run.ideas_count}'})}\n\n"

            if run.status == 'completed':
                yield f"data: {json.dumps({'timestamp': time.time(), 'message': f'✓ Successfully generated {run.ideas_count} ideas!', 'type': 'success'})}\n\n"
                yield f"data: {json.dumps({'timestamp': time.time(), 'message': 'Generation complete. Redirecting...', 'type': 'success'})}\n\n"
                break
            elif run.status == 'failed':
                yield f"data: {json.dumps({'timestamp': time.time(), 'message': f'ERROR: {run.error_message}', 'type': 'error'})}\n\n"
                break
            else:
                # Send a log message every few seconds
                if log_index < len(log_messages):
                    yield f"data: {json.dumps({'timestamp': time.time(), 'message': log_messages[log_index]})}\n\n"
                    log_index += 1
                else:
                    # Repeat some generic messages
                    yield f"data: {json.dumps({'timestamp': time.time(), 'message': 'Processing... Please wait...'})}\n\n"

            await asyncio.sleep(3)

    return StreamingResponse(
        log_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/runs/{run_id}/ideas")
async def get_ideas(run_id: str, db: Session = Depends(get_db)):
    """Get all ideas for a completed run"""
    run = get_run_status(db, run_id)

    if not run:
        raise HTTPException(status_code=404, detail="Прогон не найден")

    if run.status != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Прогон еще не завершен. Текущий статус: {run.status}"
        )

    ideas = get_run_ideas(db, run_id)

    return {
        "run_id": run_id,
        "ideas_count": len(ideas),
        "selected_direction": run.selected_direction,
        "optional_direction": run.optional_direction,
        "ideas": [idea.to_dict_brief() for idea in ideas]
    }
