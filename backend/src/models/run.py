from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from . import Base


class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default='pending')  # pending, running, completed, failed
    current_stage = Column(String(100), nullable=True)
    optional_direction = Column(String(500), nullable=True)
    ideas_count = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)

    # Relationships
    ideas = relationship("Idea", back_populates="run", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'run_id': self.id,
            'status': self.status,
            'current_stage': self.current_stage,
            'progress_percent': self._calculate_progress(),
            'optional_direction': self.optional_direction,
            'ideas_count': self.ideas_count,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def _calculate_progress(self):
        """Calculate approximate progress percentage based on stage"""
        stage_progress = {
            'Поиск сигналов': 20,
            'Анализ болей': 40,
            'Генерация идей': 60,
            'Поиск аналогов': 80,
            'Создание планов': 90,
            'Завершение': 100
        }
        return stage_progress.get(self.current_stage, 0)
