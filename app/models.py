# -*- coding: utf8 -*-

from hashlib import md5
import re
import json as simplejson
from app import db
from app import app
from config import WHOOSH_ENABLED, TIME_FORMAT, IMAGE_STORAGE_PATH
from text_utils import *

import sys

if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = WHOOSH_ENABLED
    if enable_search:
        import flask.ext.whooshalchemy as whooshalchemy

"""
    Not sure if we really need following_topics and paid_topics. However, using only one
    caused errors in the unit test. Maybe using two is the right way. We should re-visit this
    later on.
"""
following_topics = db.Table(
    'following_topics',
    db.Column('customer_id', db.Integer, db.ForeignKey('customer.user_id')),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.topic_id'))
)

paid_topics = db.Table(
    'paid_topics',
    db.Column('customer_id', db.Integer, db.ForeignKey('customer.user_id')),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.topic_id'))
)

"""
    The many-to-many relationship between customers and experts. A customer following an expert
    means that customer shows interests in that expert. That does not mean the customer is
    requesting service from that expert. This serves as a bookmarking function.
"""
following_experts = db.Table(
    'following_experts',
    db.Column('customer_id', db.Integer, db.ForeignKey('customer.user_id')),
    db.Column('expert_id', db.Integer, db.ForeignKey('expert.user_id'))
)

"""
    The many-to-many relationship between experts and skill category tags.
"""
category_tags = db.Table(
    'category_tags',
    db.Column('expert_id', db.Integer, db.ForeignKey('expert.user_id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.category_id'))
)

"""
    The many-to-many relationship between base users and comments. One user could have multiple comments, but one comment just maps to 2 users, fromuser and touser.
"""
user_comments = db.Table(
    'user_comments',
    db.Column('user_id', db.Integer, db.ForeignKey('base_user.user_id')),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.comment_id'))
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
    phone_number = db.Column(db.String(20), index=True, unique=True)
    comments = db.relationship('Comment', secondary=user_comments, backref=db.backref('base_user', lazy='dynamic'), lazy='dynamic')

    def add_comment(self, comment):
        if not self.has_comment(comment):
            self.comments.append(comment)
            return self

    def remove_comment(self, comment):
        if self.has_comment(comment):
            self.comments.remove(comment)
            return self

    def has_comment(self, comment):
        return self.comments.filter(user_comments.c.comment_id == comment.comment_id).count() > 0

    """
	Serialize the current object to json
    """
    """
    return full content including comments to meet user query
    """
    def serialize(self):
        return {
            'user_id': self.user_id, 
	    'name': self.name,
            'email': self.email,
	    'last_seen': self.last_seen.strftime(TIME_FORMAT),
	    'company': self.company,
	    'title': self.title,
	    'about_me': self.about_me,
		'phone_number': self.phone_number,
        'comments': serialize_all(self.comments, Comment.serialize_s)
	}

	__mapper_args__ = {
        'polymorphic_identity':'base_user',
        'polymorphic_on':type,
		'with_polymorphic':'*'
    }

	"""
    return partial content excluding comments to meet comment query
    """
    def serialize_s(self):
        return {
            'user_id': self.user_id, 
	    'name': self.name,
            'email': self.email,
	    'last_seen': self.last_seen.strftime(TIME_FORMAT),
	    'company': self.company,
	    'title': self.title,
	    'about_me': self.about_me,
		'phone_number': self.phone_number
	}

"""
    Customers pay expert to get services.
"""
class Customer(BaseUser):
    __tablename__ = 'customer'
    user_id = db.Column(db.Integer, db.ForeignKey('base_user.user_id'), primary_key=True)
    #comment phone_number, move it to User class
	#phone_number = db.Column(db.String(20), index=True, unique=True)

    following_topics = db.relationship(
	'Topic',
	secondary = following_topics,
        backref = db.backref('following_customers', lazy = 'dynamic'),
	lazy = 'dynamic'
    )

    paid_topics = db.relationship(
	'Topic',
	secondary = paid_topics,
        backref = db.backref('paid_customers', lazy='dynamic'),
	lazy = 'dynamic'
    )
    """
    following_experts = db.relationship(
	'Expert',
	secondary = following_experts,
        backref = db.backref('following_customers', lazy='dynamic'),
	lazy = 'dynamic'
    )
    """

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
        return self.following_topics.filter(following_topics.c.topic_id == topic.topic_id).count() > 0

    def is_paid(self, topic):
        return self.paid_topics.filter(paid_topics.c.topic_id == topic.topic_id).count() > 0
 
    """
	Serialize the current object into json
    """
    def serialize(self):
	json_obj = super(Customer, self).serialize()
	json_obj['phone_number'] = self.phone_number
	json_obj['following_topics'] = serialize_all(self.following_topics, Topic.serialize)
	json_obj['paid_topics'] = serialize_all(self.paid_topics, Topic.serialize)
        return json_obj

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
    profile_thumbnail_url = db.Column(db.String(250))
    profile_image_url = db.Column(db.String(250))
    profile_image_url = db.Column(db.String(250))
    bio = db.Column(db.String(1000))
    credits = db.Column(db.Integer)
    """
	A one-to-many relationship exists between an expert and topics.
    """
    serving_topics = db.relationship('Topic', backref='expert', lazy='dynamic')

    category_tags = db.relationship(
	'Category',
	secondary = category_tags,
        backref = db.backref('experts', lazy='dynamic'),
	lazy = 'dynamic'
    )

    __mapper_args__ = {
        'polymorphic_identity':'expert',
    }

    """
	Remove a topic.
	@param topic
    """
    def remove_topic(self, topic):
        if self.has_topic(topic):
            self.serving_topics.remove(topic)
            return self

    """
	Add a topic.
	@param topic
    """
    def add_topic(self, topic):
        if not self.has_topic(topic):
            self.serving_topics.append(topic)
            return self

    def add_category(self, category):
        if not self.has_category(category):
            self.category_tags.append(category)
            return self

    def remove_category(self, category):
        if self.has_category(category):
            self.category_tags.remove(category)
            return self

    def has_category(self, category):
        return self.category_tags.filter(category_tags.c.category_id == category.category_id).count() > 0
  
    def make_category(self, first_level_index, second_level_index):
        return Category(first_level_index, second_level_index)
 
    """
	Check if this expert is already serving this topic
    """
    def has_topic(self, topic):
        return self.serving_topics.filter_by(topic_id = topic.topic_id).count() > 0

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

	"""
	Serialize the current object into json
    """
    def serialize(self):
	json_obj = super(Expert, self).serialize()
	json_obj['degree'] = self.degree
	json_obj['serving_topics'] = serialize_all(self.serving_topics, Topic.serialize)
        return json_obj
		
    """
    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
            (md5(self.email.encode('utf-8')).hexdigest(), size)

    def followed_posts(self):
        return Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Post.timestamp.desc())

    """

"""
    Experts serve customers via Topic. In other words, an expert could provide multiple
    topics to serve customers. Each topic has its own cost. A customer can buy multiple
    topics, the service of each of which is in the form of an in-app audio conversation.

    Intuitively, a topic is a service focusing on a specific area that an expert provides.
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

    @staticmethod
    def serialize(topic):
	return {
	    'topic_id' : topic.topic_id,
        'title' : topic.title,
	    'body' : topic.body,
	    'timestamp' : topic.timestamp.strftime(TIME_FORMAT),
	    'rate' : topic.rate,
	    'expert_id' : topic.expert_id
	}

"""
    The skill categories of an expert, represented by the indices into the category text.
    A two-level category hierarchy is currently being used.
    The category hierarchy is specified in the expert_categories.txt file

    The first level category index can be obtained by category_id / 100
    The second level category index can be obtained by category_id % 100
"""
class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True) 

    def __init__(self, first_level_index, second_level_index):
	self.category_id = first_level_index * 100 + second_level_index

if enable_search:
    whooshalchemy.whoosh_index(app, Topic)

"""
    Represents the Comment object. One user could own multiple comments, and one comment just belongs to two users.
"""
class Comment(db.Model):
    __tablename__ = 'comment'
    comment_id = db.Column(db.Integer, primary_key=True)
    comment_content = db.Column(db.String(1000))
    users = db.relationship('BaseUser', secondary=user_comments, backref=db.backref('comment', lazy='dynamic'), lazy='dynamic')

    def add_user(self, user):
        if not self.has_user(user):
            self.users.append(user)
            return self

    def remove_user(self, user):
        if self.has_user(user):
            self.users.remove(user)
            return self

    def has_user(self, user):
        return self.users.filter(user_comments.c.user_id == user.user_id).count() > 0    

    def serialize_s(self):
        return {
            'comment_id': self.comment_id,
            'comment_content': self.comment_content
    }

    def serialize(self):
        return {
            'comment_id': self.comment_id,
            'comment_content': self.comment_content,
            'users': serialize_all(self.users, BaseUser.serialize_s)
    }

    def __repr__(self):
        return '<Comment %r>' % (self.comment_content)

"""
    Represents the InstructionModule object.
"""
class Instruction(db.Model):
    __tablename__ = 'instruction'
    instruction_id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String(100))
    image_url = db.Column(db.String(250))

    def serialize(self):
        return {
            "instruction_id": self.instruction_id,
            "header": self.header,
			"image_url": IMAGE_STORAGE_PATH + self.image_url
    }	