from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class Evidence(Base):
    __tablename__ = "evidences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_id = Column(Integer, ForeignKey('ideas.id', ondelete='CASCADE'), nullable=False)
    pattern_description = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False)
    source_url = Column(String(500), nullable=True)
    example_quote = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    idea = relationship("Idea", back_populates="evidences")

    def to_dict(self):
        return {
            'id': self.id,
            'pattern_description': self.pattern_description,
            'source_type': self.source_type,
            'source_url': self.source_url,
            'example_quote': self.example_quote
        }
