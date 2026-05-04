import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Idea(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'ideas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)
    joke = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    is_published = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.datetime.now)

    # Внешние ключи
    author_id = Column(Integer, ForeignKey('users.id'))
    source_idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=True)

    # Связи
    author = relationship("User", foreign_keys=[author_id], back_populates="published_ideas")
    favorited_by = relationship("User", secondary="favorite_ideas", back_populates="favorite_ideas")

    def __repr__(self):
        return f"<Idea> {self.title} ({self.category})"