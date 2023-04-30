import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase, create_session
from .likes import Like


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    def get_likes(self):
        db_sess = create_session()
        like = db_sess.query(Like).filter(Like.post_id == self.id,
                                          Like.is_like == True).count()
        db_sess.close()
        return like

    def get_dislikes(self):
        db_sess = create_session()
        dislike = db_sess.query(Like).filter(Like.post_id == self.id,
                                          Like.is_like == False).count()
        db_sess.close()
        return dislike

    def get_diff_likes_dislikes(self):
        return self.get_likes() - self.get_dislikes()

    def __lt__(self, other):
        return self.get_diff_likes_dislikes() < other.get_diff_likes_dislikes()

    def __eq__(self, other):
        return self.get_diff_likes_dislikes() == other.get_diff_likes_dislikes()
