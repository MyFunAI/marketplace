from hashlib import md5
import re
from app import db
from app import app
from config import WHOOSH_ENABLED

import sys
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = WHOOSH_ENABLED
    if enable_search:
        import flask.ext.whooshalchemy as whooshalchemy

topics = db.Table(
    'topics',
    db.Column('customer_id', db.Integer, db.ForeignKey('customer.user_id')),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.topic_id'))
)

"""
    The base class for users.
    Experts and non-experts (who pay to talk to experts) inherit from this class. 
"""
class BaseUser(db.Model):
    __tablename__ = 'base_user'
    """
    categories = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')
    """
    user_id = db.Column(db.Integer, index = True, primary_key = True)
    email = db.Column(db.String(120), index=True, unique=True)
    last_seen = db.Column(db.DateTime)
    name = db.Column(db.String(10), index = True)
    company = db.Column(db.String(50), index = True)
    title = db.Column(db.String(20), index = True)  #CEO, VP, etc.
    about_me = db.Column(db.String(500))


"""
    Customers pay expert to get services.
"""
class Customer(BaseUser):
    __tablename__ = 'customer'
    user_id = db.Column(db.Integer, db.ForeignKey('base_user.user_id'), primary_key=True)
    phone_number = db.Column(db.String(20), index=True, unique=True)

    following_topics = db.relationship(
	'Topic',
	secondary = topics,
        backref = db.backref('following_customers', lazy = 'dynamic'),
	lazy = 'dynamic'
    )

    paid_topics = db.relationship(
	'Topic',
	secondary = topics,
        backref = db.backref('paid_customers', lazy='dynamic'),
	lazy = 'dynamic'
    )
    
    def follow_topic(self, topic):
        if not self.is_following(topic):
            self.following_topics.append(topic)
            return self

    def unfollow_topic(self, topic):
        if self.is_following(topic):
            self.following_topics.remove(topic)
            return self

    def add_paid_topic(self, topic):
        if not self.is_paid(topic):
            self.paid_topics.append(topic)
            return self

    def remove_paid_topic(self, topic):
        if self.is_paid(topic):
            self.paid_topics.remove(topic)
            return self

    def is_following(self, topic):
        return self.following_topics.filter(topics.c.topic_id == topic.topic_id).count() > 0

    def is_paid(self, topic):
        return self.paid_topics.filter(topics.c.topic_id == topic.topic_id).count() > 0

"""
    Experts are paid to provide consulting services.
"""
class Expert(BaseUser):
    __tablename__ = 'expert'
    user_id = db.Column(db.Integer, db.ForeignKey('base_user.user_id'), primary_key=True)
    degree = db.Column(db.String(10))  #Ph.D., M.S., M.B.A., etc.
    university = db.Column(db.String(50))  #University name
    major = db.Column(db.String(50))  #degree, university and major are usually used together
    rating = db.Column(db.Float)  #rating of this expert based on the feedback from the customers
    needed_count = db.Column(db.Integer)  #the number of customers hoping to talk to this expert
    serving_count = db.Column(db.Integer)  #times this expert served customers
    category_1_index = db.Column(db.Integer)  #top level category, the category hierarchy is specified in the expert_categories.txt file
    category_2_index = db.Column(db.Integer)  #second level category

    """
	A one-to-many relationship exists between an expert and topics.
    """
    serving_topics = db.relationship('Topic', backref='expert', lazy='dynamic')

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub('[^a-zA-Z0-9_\.]', '', nickname)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
            (md5(self.email.encode('utf-8')).hexdigest(), size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Post.timestamp.desc())

    def __repr__(self):  # pragma: no cover
        return '<User %r>' % (self.nickname)

"""
    Experts serve customers via Topic. In other words, an expert could provide multiple
    topics to serve customers. Each topic has its own cost. A customer can buy multiple
    topics, the service of each of which is in the form of an in-app audio conversation.
"""
class Topic(db.Model):
    __tablename__ = 'topic'
    __searchable__ = ['body']

    topic_id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    title = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)
    rate = db.Column(db.Float)  #how much this topic costs
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.user_id'))

    def __repr__(self):  # pragma: no cover
        return '<Topic %r>' % (self.body)

if enable_search:
    whooshalchemy.whoosh_index(app, Topic)
