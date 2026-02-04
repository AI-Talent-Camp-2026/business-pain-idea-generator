from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey('runs.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(200), nullable=False)
    pain_description = Column(Text, nullable=False)
    segment = Column(String(200), nullable=False)
    confidence_level = Column(String, nullable=False)  # high, medium, low
    brief_evidence = Column(Text, nullable=False)
    detailed_evidence = Column(Text, nullable=True)  # JSON
    plan_7days = Column(Text, nullable=False)
    plan_30days = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    run = relationship("Run", back_populates="ideas")
    analogues = relationship("Analogue", back_populates="idea", cascade="all, delete-orphan")
    evidences = relationship("Evidence", back_populates="idea", cascade="all, delete-orphan")

    def to_dict_brief(self):
        """Brief representation for ideas list"""
        return {
            'id': self.id,
            'title': self.title,
            'pain_description': self.pain_description[:200] + '...' if len(self.pain_description) > 200 else self.pain_description,
            'segment': self.segment,
            'confidence_level': self.confidence_level,
            'brief_evidence': self.brief_evidence
        }

    def to_dict_full(self):
        """Full representation for idea details"""
        return {
            'id': self.id,
            'title': self.title,
            'pain_description': self.pain_description,
            'segment': self.segment,
            'confidence_level': self.confidence_level,
            'brief_evidence': self.brief_evidence,
            'detailed_evidence': self.detailed_evidence,
            'analogues': [analogue.to_dict() for analogue in self.analogues],
            'plan_7days': self.plan_7days,
            'plan_30days': self.plan_30days
        }
