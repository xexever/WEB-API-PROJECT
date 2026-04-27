import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    about = Column(String, nullable=True)
    email = Column(String, index=True, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    news = orm.relationship("News", back_populates='user')
    avatar = Column(String, nullable=True, default='/static/default_avatar.png')

    def __repr(self):
        return f"<User> {self.name} {self.about} {self.email}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
