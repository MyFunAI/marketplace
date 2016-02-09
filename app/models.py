# -*- coding: utf8 -*-

from app import db
from app import app
from config import WHOOSH_ENABLED, TIME_FORMAT, INSTRUCTION_IMAGE_PATH, CUSTOMER_TYPE, EXPERT_TYPE
from hashlib import md5
from model_utils import *
from text_utils import *
import json as simplejson
import re
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
    The many-to-many relationship between people who comment and who are commented.
    In our case, only experts can be commented, but both customers and experts can
    make comments.

    No customers have identical ids as experts. So this table has no duplicate rows.
"""
commenters = db.Table('commenters',
    db.Column('commenter_id', db.Integer, db.ForeignKey('base_user.id')),
    db.Column('commentee_id', db.Integer, db.ForeignKey('base_user.id'))
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
    type = db.Column(String(50))

    """
	Commenting is a self-referential relationship, which captures the sending and receiving ends of a comment. The content
	of the comment is stored in class Comment.

	The current user is the target user.
	primaryjoin indicates the condition that links the left side entity (the commenter user) with the association table.
	Note that because the commenters table is not a model there is a slightly odd syntax required to get to the field name.
	secondaryjoin indicates the condition that links the right side entity (the commentee user) with the association table.

	backref defines how this relationship will be accessed from the right side entity. We said that for a given user
	the query named commentees returns all the right side users that have the target user on the left side.
	The back reference will be called commenters and will return all the left side users that are linked to the target user
	in the right side.
    """
    commentees = db.relationship(
	'BaseUser', 
	secondary = commenters,
	primaryjoin = (commenters.c.commenter_id == user_id), 
        secondaryjoin = (commenters.c.commentee_id == user_id), 
        backref = db.backref('commenters', lazy='dynamic'), 
        lazy='dynamic'
    )

    def comment(self, user):
        if not self.has_commented(user):
            self.commentees.append(user)
            return self

    def uncomment(self, user):
        if self.has_commented(user):
            self.commentees.remove(user)
            return self

    def has_commented(self, user):
        return self.commentees.filter(commenters.c.commentee_id == user.user_id).count() > 0

    """
	Serialize comments
    """
    def serialize_comments(self):
	pass

    """
	Serialize the current object to json
    """
    def serialize(self):
        return {
            'user_id': self.user_id, 
	    'name': self.name,
            'email': self.email,
	    'last_seen': self.last_seen.strftime(TIME_FORMAT),
	    'company': self.company,
	    'title': self.title,
	    'about_me': self.about_me
	}

    __mapper_args__ = {
        'polymorphic_identity':'base_user',
        'polymorphic_on':type,
	'with_polymorphic':'*'
    }

"""
    Customers pay expert to get services.
"""
class Customer(BaseUser):
    __tablename__ = 'customer'
    user_id = db.Column(db.Integer, db.ForeignKey('base_user.user_id'), primary_key=True)
    #Experts do not provide a phone number to avoid direct contact between customers and experts
    phone_number = db.Column(db.String(20), index=True, unique=True)

    __mapper_args__ = {
        'polymorphic_identity':'customer',
    }

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
	For Customer objects, this method only loads the comments this customer made.
    """
    def load_comments(self):
	return Comment.query.join(commenters, (commenters.c.commenter_id == Comment.src_user_id)).filter(commenters.c.commenter_id == self.user_id).order_by(Comment.timestamp.desc())
 
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
    bio = db.Column(db.Text(1000))
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

    """
	Check if this expert is already serving this topic
    """
    def has_topic(self, topic):
        return self.serving_topics.filter_by(topic_id = topic.topic_id).count() > 0

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
	For experts, they can comment or be commented by other experts.

	@param forward
		True: the current user is the commenting user, False: the current user is the commented user
	@param src_user_type
		1: customer, 2: expert
	@return
    """
    def load_comments(self, forward = True, src_user_type = 1):
	if forward:
	    #Commenting other experts
	    return Comment.query.join(commenters, (commenters.c.commenter_id == Comment.src_user_id)).filter(commenters.c.commenter_id == self.user_id).order_by(Comment.timestamp.desc())
	else:
	    #being commented by customers or experts
	    return Comment.query.join(commenters, (commenters.c.commenter_id == Comment.src_user_id)).filter(commenters.c.commentee_id == self.user_id).filter(Comment.src_user_type == src_user_type).order_by(Comment.timestamp.desc())

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
    #rating = db.Column(db.Float) #the average customer rating on this topic 

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
    We only offer two commenting behaviors for the moment: customers comment experts, experts comment experts.

    In an expert object, there are comments made on that expert by customers and other experts. Comments originating
    from that expert are not saved in that expert object.

    In a customer object, comments made by that customer are not present in the object.
"""
class Comment(db.Model):
    __tablename__ = 'comment'
    """
        TO-DO: could use a pairing function to compute an int key
	    Currently, the comment_id is a string in the format 'src_user_id:dst_user_id', with the two parts indicating
	    the user making the comment and the user being commented.
    """
    comment_id = db.Column(db.String, primary_key=True)
    content = db.Column(db.Text(1000))
    timestamp = db.Column(db.Date)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.topic_id'))
    src_user_id = db.Column(db.Integer, db.ForeignKey('base_user.user_id'))
    dst_user_id = db.Column(db.Integer, db.ForeignKey('base_user.user_id'))
    src_user_type = db.Column(db.Integer)
    dst_user_type = db.Column(db.Integer)

    def serialize(self):
        return {
            'comment_id': self.comment_id,
            'content': self.content,
	    'timestamp': self.timestamp.strftime(DATE_FORMAT),
	    'topic_id' : self.topic_id,
	    'src_user_id' : self.src_user_id,
	    'dst_user_id' : self.dst_user_id,
    	    'src_user_type' : self.src_user_type,
    	    'dst_user_type' : self.dst_user_type
        }

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
	    "image_url": INSTRUCTION_IMAGE_PATH + self.image_url
    }
