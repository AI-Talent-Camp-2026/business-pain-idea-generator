from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from . import Base


class Analogue(Base):
    __tablename__ = "analogues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idea_id = Column(Integer, ForeignKey('ideas.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    url = Column(String(500), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)

    # Relationships
    idea = relationship("Idea", back_populates="analogues")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url
        }
