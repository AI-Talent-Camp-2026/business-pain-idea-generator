from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    run_id = Column(String, ForeignKey('runs.id'), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_ip = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Relationships
    idea = relationship("Idea", back_populates="purchases")

    def to_dict(self):
        return {
            'id': self.id,
            'idea_id': self.idea_id,
            'idea_title': self.idea.title if self.idea else None,
            'run_id': self.run_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_ip': self.user_ip
        }
