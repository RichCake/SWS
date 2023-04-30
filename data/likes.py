import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Like(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'likes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('news.id'))
    is_like = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    user = orm.relationship('User')
    news = orm.relationship('News')
