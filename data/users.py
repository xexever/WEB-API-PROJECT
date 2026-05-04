import datetime
from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

# Таблица для связи "избранное" (многие ко многим) - ТОЛЬКО ЗДЕСЬ
favorite_ideas = Table(
    'favorite_ideas',
    SqlAlchemyBase.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('idea_id', Integer, ForeignKey('ideas.id'))
)


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    about = Column(String, nullable=True)
    email = Column(String, index=True, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    avatar = Column(String, nullable=True, default='/static/default_avatar.png')

    # Связи
    news = orm.relationship("News", back_populates='user')
    published_ideas = orm.relationship("Idea", foreign_keys='Idea.author_id', back_populates='author')
    favorite_ideas = orm.relationship("Idea", secondary=favorite_ideas, back_populates='favorited_by')

    def __repr__(self):
        return f"<User> {self.name} {self.about} {self.email}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)