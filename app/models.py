# -*- coding: utf8 -*-

from app import db
from app import app
from config import *
from datetime import datetime
#from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
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

paid_topics = db.Table(
    'paid_topics',
    db.Column('customer_id', db.Integer, db.ForeignKey('customer.user_id')),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.topic_id'))
)

"""
    The many-to-many relationship between customers/experts and experts. A customer/expert
    following an expert means that customer/expert shows interests in that expert. That does
    not mean the customer is requesting service from that expert. This serves as a bookmarking
    function.
"""
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('base_user.user_id')),
    db.Column('followee_id', db.Integer, db.ForeignKey('base_user.user_id'))
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
    The base class for users.
    Experts and non-experts (who pay to talk to experts) inherit from this class.

    Actual usage will not instantiate this class, and will use Customer and Expert class only.
"""
class BaseUser(db.Model):
    __tablename__ = 'base_user'
    user_id = db.Column(db.Integer, index = True, primary_key = True)
    email = db.Column(db.String(120), index=True, unique=True)
    last_seen = db.Column(db.DateTime)
    name = db.Column(db.String(10), index = True)
    company = db.Column(db.String(50), index = True)
    title = db.Column(db.String(20), index = True)  #CEO, VP, etc.
    about_me = db.Column(db.String(500))
    avatar_thumbnail_url = db.Column(db.String(250))
    avatar_url = db.Column(db.String(250))
    type = db.Column(db.String(20))

    """
	Users that the current user shows interests. The current user is the target user, i.e., this user object.
	Showing interests is not the same as requesting services.
    """
    followees = db.relationship(
	'BaseUser', 
	secondary = followers,
	primaryjoin = (followers.c.follower_id == user_id), 
        secondaryjoin = (followers.c.followee_id == user_id), 
        backref = db.backref('followers', lazy='dynamic'), 
        lazy = 'dynamic'
    )

    def is_following_expert(self, user):
        return user and user.is_expert() and (self.followees.filter(followers.c.followee_id == user.user_id).count() > 0)

    def follow_expert(self, user):
        if user and user.is_expert() and not self.is_following_expert(user):
            self.followees.append(user)
            return self

    def follow_expert_by_id(self, user_id):
        user = Expert.query.filter_by(user_id = user_id).first()
	self.follow_expert(user)

    def unfollow_expert(self, user):
        if user.is_expert() and self.is_following_expert(user):
            self.followees.remove(user)
            return self

    """
	Get the number of experts the current user is interested in.
    """
    def get_followee_count(self):
	return self.followees.count()

    """
	Get the number of people that show interests on the current user.
    """
    def get_follower_count(self):
	return self.followers.count()

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
	    'about_me': self.about_me,
            'avatar_thumbnail_url': self.avatar_thumbnail_url,
	    'avatar_url': self.avatar_url
	}

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
            return unicode(self.user_id)  # python 2
        except NameError:
            return str(self.user_id)  # python 3


    __mapper_args__ = {
        'polymorphic_identity':'base_user',
        'polymorphic_on':type,
	'with_polymorphic':'*'
    }

"""
    Customers pay experts to get services.
"""
class Customer(BaseUser):
    __tablename__ = 'customer'
    user_id = db.Column(db.Integer, db.ForeignKey('base_user.user_id'), primary_key = True)
    #Experts do not provide a phone number to avoid direct contact between customers and experts
    phone_number = db.Column(db.String(20), index = True, unique = True)

    __mapper_args__ = {
        'polymorphic_identity':'customer',
    }

    def is_expert(self):
	return False

    """
	One to many relationship. One customer could have multiple topic requests.
	Ongoing and completed requests are mingled together.
	An ongoing request is one that has not passed the 'served' stage.
	A topic goes through all stages except for the 'customer rating' and is then marked 'completed'.
    """
    topic_requests = db.relationship(
	'TopicRequest',
	backref = 'customer',
	lazy = 'dynamic'
    )

    """
    completed_topic_requests = db.relationship(
	'TopicRequest',
	backref = 'completed_customer',
	lazy = 'dynamic'
    )
    """
    #def load_topic_requests(self):
	#self.topic_requests = TopicRequest.query.filter_by(customer_id = self.user_id).all()

    """
	@return a list of this customer's ongoing requests
    """
    def get_ongoing_requests(self):
	return [r for r in self.topic_requests.all() if not r.is_completed()]

    """
	@return a list of this customer's completed requests
    """
    def get_completed_requests(self):
	return [r for r in self.topic_requests.all() if r.is_completed()]

    """
	@param topic - a given topic, an instance of the Topic class
	@return one or no ongoing request for the given topic
    """
    def get_ongoing_requests_by_topic(self, topic):
        requests = self.topic_requests.filter_by(topic_id = topic.topic_id).all()
	if requests:
	    return [r for r in requests if not r.is_completed()]
	else:
	    return []

    """
	Check if the current customer can request the given topic, i.e., the topic is not already being
	requested by the current customer.

	@param topic - the topic being requested, an instance of a Topic class
    """
    def is_topic_being_requested(self, topic):
        #return self.ongoing_topic_requests.filter_by(topic_id = topic.topic_id).count() > 0
        return len(self.get_ongoing_requests_by_topic(topic)) > 0

    """
	Remove a topic request from the ongoing request list.
	TO-DO: add more check conditions, e.g., a request can be dropped if it is in certain stages.
	@param topic - a Topic instance
    """
    def remove_topic_request(self, topic):
        #r = self.ongoing_topic_requests.filter_by(topic_id = topic.topic_id).first()
        ongoing_topics = self.get_ongoing_requests_by_topic(topic)
	if len(ongoing_topics) > 0:
            self.topic_requests.remove(ongoing_topics[0])
            return self

    """
	Request a topic for the current customer, adding it to the ongoing request list.
	@param topic - a Topic instance
    """
    def add_topic_request(self, topic):
        if not self.is_topic_being_requested(topic):
	    r = TopicRequest(
    		customer_id = self.user_id,
    		topic_id = topic.topic_id,
		topic = topic
	    )
	    r.init_stage()
            self.topic_requests.append(r)
            return self

    """
	Load the experts that the current customer showed interests in.
	@param a query object of the needed experts 
    """
    def load_followed_experts(self):
	expert_ids = [expert.user_id for expert in self.followees.all()]
	return Expert.query.filter(Expert.user_id.in_(expert_ids))

    """
	Serialize fields except for the interested-in experts.
    """
    def serialize_simple(self):
	json_obj = super(Customer, self).serialize()
	json_obj['phone_number'] = self.phone_number
	experts = self.load_followed_experts().all()
	json_obj['interested_in_expert_count'] = len(experts)
	json_obj['completed_topic_requests'] = [r.serialize() for r in self.topic_requests.all() if r.is_completed()] 
	json_obj['ongoing_topic_requests'] = [r.serialize() for r in self.topic_requests.all() if not r.is_completed()] 
	return json_obj

    """
	Serialize the current object into json. All fields of the object are fully rendered as well.
    """
    def serialize(self):
	json_obj = super(Customer, self).serialize()
	json_obj['phone_number'] = self.phone_number
	experts = self.load_followed_experts().all()
	json_obj['interested_in_experts'] = [e.serialize_simple() for e in experts]
	json_obj['interested_in_expert_count'] = len(experts)
	json_obj['completed_topic_requests'] = [r.serialize() for r in self.topic_requests.all() if r.is_completed()] 
	json_obj['ongoing_topic_requests'] = [r.serialize() for r in self.topic_requests.all() if not r.is_completed()] 
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
    #needed_count = db.Column(db.Integer)  #the number of customers hoping to talk to this expert
    #serving_count = db.Column(db.Integer)  #times this expert served customers
    bio = db.Column(db.Text(2000))
    credits = db.Column(db.Integer)

    """
	A one-to-many relationship exists between an expert and topics.
    """
    serving_topics = db.relationship('Topic', backref='expert', lazy='joined')

    tags = db.relationship(
	'Category',
	secondary = category_tags,
        backref = db.backref('experts', lazy='dynamic'),
	lazy = 'joined'
    )

    __mapper_args__ = {
        'polymorphic_identity':'expert',
    }

    def is_expert(self):
	return True

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
        #return self.serving_topics.filter_by(topic_id = topic.topic_id).count() > 0
	for t in self.serving_topics:
	    if t.topic_id == topic.topic_id:
		return True
	return False

    def add_tag(self, tag):
        if not self.has_tag(tag):
            self.tags.append(tag)
            return self

    def remove_tag(self, tag):
        if self.has_tag(tag):
            self.tags.remove(tag)
            return self

    """
	Search the tag given a Category object or the two-level indices.
	TO-DO:
	    Find the most matching category given textual description of the skills. This is the real-life
	    scenarios where our marketplace users simply search expert skills.
	@param tag - a Category object
	@param first_level_index
	@param second_level_index
    """
    def has_tag(self, tag = None, first_level_index = -1, second_level_index = -1):
	if tag:
            #return self.tags.filter(category_tags.c.category_id == tag.category_id).count() > 0
	    for t in self.tags:
		if tag.category_id == t.category_id:
		    return True
	    return False
	else:
            category_id = build_category_id(first_level_index, second_level_index)
            #return self.tags.filter(category_tags.c.category_id == category_id).count() > 0
	    for t in self.tags:
		if category_id == t.category_id:
		    return True
	    return False
 
    def build_category(self, first_level_index, second_level_index):
        return Category(build_category_id(first_level_index, second_level_index))

    """
	Mark a topic request as 'complete'.
	This action is triggered by experts only.
	@param request - a TopicRequest instance
    """
    def complete_request(self, request):
	if self.has_topic(request.topic):
	    request.set_to_completed()

    """
	Comments are associated with topic requests, which can be found in topic objects.
	To fetch the comments, go through the following steps
	1) Start from each of the topics being served by the current expert
	2) Get all the topic requests of each topic
	3) If that topic request has a comment associated with it, retrieve it

	TO-DO: add caching to avoid unnecessary accesses to the db
	@return a list of comments
    """
    def get_comments(self):
	comments = []
	for topic in self.serving_topics:
	    for request in topic.topic_requests.all():
		if request.is_rated():
		    comments.append(request.comment)
	return comments

    """
	Get the customers that this expert has served.
	To fetch the customers, go through the following steps
	1) Start from each of the topics being served by the current expert
	2) Get all the 'completed' topic requests of each topic
	3) Get the customers associated with those topic requests

	TO-DO: add caching to avoid unnecessary accesses to the db
	@return a list of customers
    """
    def get_served_customers(self):
	customers = []
	for topic in self.serving_topics:
	    for request in topic.topic_requests.all():
		if request.is_completed():
		    customers.append(request.customer)
	return customers

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

    """
	Load the customers that have shown interests in this expert.
	@return a query object of the needed customers
    """
    def load_following_customers(self):
	customer_ids = [customer.user_id for customer in self.followers.all()]
	return Customer.query.filter(Customer.user_id.in_(customer_ids))

    """
	Serialize the fields except for the following customers.
    """
    def serialize_simple(self):
	customers = self.load_following_customers().all()
	json_obj = super(Expert, self).serialize()
	json_obj['degree'] = self.degree
	json_obj['serving_topics'] = [r.serialize() for r in self.serving_topics]
        json_obj['university'] = self.university 
	json_obj['major'] = self.major
        json_obj['rating'] = self.rating
        json_obj['bio'] = self.bio
	json_obj['credits'] = self.credits
	json_obj['comments'] = [c.serialize() for c in self.get_comments()]
	json_obj['following_customer_count'] = len(customers)
        return json_obj

    """
	Serialize the current object into json
    """
    def serialize(self):
	customers = self.load_following_customers().all()
	json_obj = super(Expert, self).serialize()
	json_obj['degree'] = self.degree
	json_obj['serving_topics'] = [r.serialize() for r in self.serving_topics]
        json_obj['university'] = self.university 
	json_obj['major'] = self.major
        json_obj['rating'] = self.rating
        json_obj['bio'] = self.bio
	json_obj['credits'] = self.credits
	json_obj['comments'] = [c.serialize() for c in self.get_comments()]
	json_obj['following_customer_count'] = len(customers)
	json_obj['following_customers'] = [c.serialize_simple() for c in customers]
	json_obj['tags'] = [t.serialize() for t in self.tags]
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
    Only customers can give ratings on topics they are served. Each topic has an average
    rating from all its serving topic.
"""
class Topic(db.Model):
    __tablename__ = 'topic'
    __searchable__ = ['body']

    topic_id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text(1000))
    title = db.Column(db.String(100))
    created_time = db.Column(db.DateTime) #the time an expert posts this topic
    rate = db.Column(db.Float)  #how much this topic costs
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.user_id'))

    """
	One-to-many relationship between Topic and TopicRequests.
    """
    topic_requests = db.relationship('TopicRequest', backref = 'topic', lazy='dynamic')

    def __repr__(self):  # pragma: no cover
        return '<Topic %r>' % (self.body)

    """
	TO-DO
	Compute an average rating for this topic based on the customers' ratings.
        Topic has a paid_customers fields
	@return
    """
    def compute_rating(self):
	s = 0.0
	if self.topic_requests:
	    n = 0
	    for r in self.topic_requests:
		if r.is_rated():
		    n += 1
		    s += r.comment.rating
	    if n > 0:
		s /= n
	return s

    """
	@return True - this request is already in this topic's request list; False - no
    """
    def has_request(self, request):
        return self.topic_requests.filter_by(request_id = request.request_id).count() > 0

    """
	Remove the given request from this topic's request list
	@param request - a TopicRequest instance
    """
    def remove_request(self, request):
        if self.has_request(request):
            self.topic_requests.remove(request)
            return self

    """
	@return a list of this topic's all ongoing requests
    """
    def get_ongoing_requests(self):
	return [r for r in self.topic_requests.all() if not r.is_completed()]

    """
	@return a list of this topic's all completed requests
    """
    def get_completed_requests(self):
	return [r for r in self.topic_requests.all() if r.is_completed()]

    def serialize(self):
	ongoing_requests = []
	completed_requests = []
	for r in self.topic_requests.all():
	    if r.is_completed():
		completed_requests.append(r)
	    else:
		ongoing_requests.append(r)
	return {
	    'topic_id' : self.topic_id,
            'title' : self.title,
	    'body' : self.body,
	    'created_time' : self.created_time.strftime(TIME_FORMAT),
	    'rate' : self.rate,
	    'expert_id' : self.expert_id,
	    'ongoing_requests_count' : len(ongoing_requests),
	    'completed_requests_count' : len(completed_requests),
	    'ongoing_requests' : [r.serialize() for r in ongoing_requests],
	    'completed_requests' : [r.serialize() for r in completed_requests],
	    'average_rating' : self.compute_rating()
	}

"""
    One-to-many relationship between Customer and TopicRequest.
    One-to-many relationship between Topic and TopicRequest.

    A topic field is added automatically by the backref in class Topic.
    A customer can request the same topic multiple times (not at the same time though), because
    one service may not fully solve the problems of that customer.
"""
class TopicRequest(db.Model):
    __tablename__ = 'topic_request'
    request_id = db.Column(db.Integer, primary_key = True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.user_id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.topic_id'))
    request_stage = db.Column(db.Integer)
    topic_requested_time = db.Column(db.DateTime)
    topic_accepted_time = db.Column(db.DateTime)
    topic_paid_time = db.Column(db.DateTime)
    topic_scheduled_time = db.Column(db.DateTime)
    topic_served_time = db.Column(db.DateTime)
    topic_rated_time = db.Column(db.DateTime)

    """
	One to one relationship between TopicRequest and Comment
    """
    comment = db.relationship('Comment', uselist = False, backref = 'topic_request')

    """
	One to many relationship between TopicRequest and Conversation
    """
    conversations = db.relationship('Conversation', backref = 'topic_request', lazy = 'dynamic')

    """
	Call this method when a TopicRequest object is created
    """
    def init_stage(self):
	self.request_stage = TOPIC_REQUESTED
	self.topic_requested_time = datetime.utcnow() 

    """
	Get the current stage of this request by the corresponding customer
    """
    def get_stage(self):
	if self.request_stage & TOPIC_REQUESTED_MASK:
	    return TOPIC_REQUESTED
	elif self.request_stage & TOPIC_ACCEPTED_MASK:
	    return TOPIC_ACCEPTED
	elif self.request_stage & TOPIC_PAID_MASK:
	    return TOPIC_PAID
	elif self.request_stage & TOPIC_SCHEDULED_MASK:
	    return TOPIC_SCHEDULED
	elif self.request_stage & TOPIC_SERVED_MASK:
	    return TOPIC_SERVED
	elif self.request_stage & TOPIC_RATED_MASK:
	    return TOPIC_RATED
	else:
	    return TOPIC_BAD_STAGE 

    """
	Move the counter to the next stage. Called after one stage is completed.
    """
    def move_to_next_stage(self):
	self.request_stage = self.request_stage << 1
	t = datetime.utcnow()
	stage = self.get_stage()
	if stage == TOPIC_ACCEPTED:
	    self.topic_accepted_time = t
	elif stage == TOPIC_PAID:
	    self.topic_paid_time = t
	elif stage == TOPIC_SCHEDULED:
	    self.topic_scheduled_time = t
	elif stage == TOPIC_SERVED:
	    self.topic_served_time = t
	elif stage == TOPIC_RATED:
	    self.topic_rated_time = t
	else:
	    self.topic_rated_time = t 
	return self.request_stage

    def is_accepted(self):
	return self.get_stage() >= TOPIC_ACCEPTED

    def is_paid(self):
	return self.get_stage() >= TOPIC_PAID

    def is_scheduled(self):
	return self.get_stage() >= TOPIC_SCHEDULED

    """
	@return True - completed; False - still going on
    """
    def is_completed(self):
	return self.get_stage() >= TOPIC_SERVED

    """
	@return True - rated and commented; False - not yet
    """
    def is_rated(self):
	return self.get_stage() >= TOPIC_RATED

    def set_to_accepted(self):
	self.request_stage = 0 | TOPIC_ACCEPTED_MASK
	self.topic_accepted_time = datetime.utcnow()

    def set_to_paid(self):
	self.request_stage = 0 | TOPIC_PAID_MASK
	self.topic_paid_time = datetime.utcnow()

    def set_to_scheduled(self):
	self.request_stage = 0 | TOPIC_SCHEDULED_MASK
	self.topic_scheduled_time = datetime.utcnow()

    """
	Set the request to the 'completed' stage, regardless of its previous stage.
    """
    def set_to_completed(self):
	self.request_stage = 0 | TOPIC_SERVED_MASK
	self.topic_served_time = datetime.utcnow()

    """
	Set the request to the 'rated' stage, regardless of its previous stage.
    """
    def set_to_rated(self):
	self.request_stage = 0 | TOPIC_RATED_MASK
	self.topic_rated_time = datetime.utcnow()

    def serialize(self):
	if self.comment:
	    comment_str = self.comment.serialize()
	else:
	    comment_str = ""
	return {
	    'request_id': self.request_id,
            'customer_id': self.customer_id,
	    'topic_id': self.topic.topic_id,
	    'topic_title': self.topic.title,
	    'expert_id': self.topic.expert_id,
	    'request_stage': self.request_stage,
	    'topic_requested_time': self.topic_requested_time,
	    'topic_accepted_time': self.topic_accepted_time,
	    'topic_paid_time': self.topic_paid_time,
	    'topic_scheduled_time': self.topic_scheduled_time,
	    'topic_served_time': self.topic_served_time,
	    'topic_rated_time': self.topic_rated_time,
	    'topic_comment': comment_str,
	    'conversations': [c.serialize() for c in self.conversations.order_by(Conversation.timestamp.desc()).all()]
	}

    """
	@param conv - a new Conversation object
	TO-DO: recalling a conversation like in WeChat
    """
    def add_conversation(self, conv):
	if self.is_conversation_on():
	    self.conversations.append(conv)
	    return self

    """
	The two parties can only chat between the paid stage and scheduled stage.
    """
    def is_conversation_on(self):
	return self.is_paid() and not self.is_scheduled()

"""
    The skill categories of an expert, represented by the indices into the category text.
    A two-level category hierarchy is currently being used.
    The category hierarchy is specified in the expert_categories.txt file

    The first level category index can be obtained by category_id / 100
    The second level category index can be obtained by category_id % 100

    TO-DO: enrich the class with textual info about the categories
"""
class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True) 

    def serialize(self):
	first_level_index = get_first_level_category_index(self.category_id)
        second_level_index = get_second_level_category_index(self.category_id)
	return {
	    'category_id' : self.category_id,
	    'first_level_index' : first_level_index,
	    'second_level_index' : second_level_index
	}

"""
    A single conversation between two users (a customer and an expert in our context).
    A one-to-many relationship exists between TopicRequest and Conversation.
"""
class Conversation(db.Model):
    __tablename__ = 'conversation'
    conversation_id = db.Column(db.Integer, primary_key = True)
    request_id = db.Column(db.Integer, db.ForeignKey('topic_request.request_id'))
    message = db.Column(db.Text(500))

    #user_1 is the src user, i.e., the one sending this message
    user_1_id = db.Column(db.Integer, db.ForeignKey('base_user.user_id'))

    #user_2 is the dst user, i.e., the one receiving this message
    user_2_id = db.Column(db.Integer, db.ForeignKey('base_user.user_id'))
    timestamp = db.Column(db.DateTime) #the time an expert posts this topic

    def serialize(self):
	return {
    	    'conversation_id' : self.conversation_id,
	    'request_id' : self.request_id,
    	    'message' : self.message,
    	    'user_1_id' : self.user_1_id,
    	    'user_2_id' : self.user_2_id,
    	    'timestamp' : self.timestamp.strftime(TIME_FORMAT)
	}

"""
    A comment corresponds to a topic request object. A customer can request the same topic multiple times (not
    at the same time though), and thus comment on the service multiple times.

    This class wraps the comments from customers to experts. A topic_request field is added automatically by the
    backref in TopicRequest. 
"""
class Comment(db.Model):
    __tablename__ = 'comment'
    comment_id = db.Column(db.String, primary_key = True)
    content = db.Column(db.Text(1000))
    request_id = db.Column(db.Integer, db.ForeignKey('topic_request.request_id'))
    rating = db.Column(db.Float)

    def serialize(self):
        return {
            'comment_id': self.comment_id,
            'content': self.content,
	    'request_id': self.request_id,
	    'rating': self.rating
        }

"""
    This class wraps the comments from experts to experts. Such comments are on an invitation basis only.

    TO-DO: to be implemented after the topic-based comments are running normally.
"""
class InvitedComment(db.Model):
    __tablename__ = 'invited_comment'
    comment_id = db.Column(db.String, primary_key = True)
    content = db.Column(db.Text(1000))
    invited_time = db.Column(db.DateTime)
    commented_time = db.Column(db.DateTime)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.user_id'))
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.user_id'))
    is_commented = db.Column(db.Boolean)    

    def serialize(self):
        return {
            'comment_id' : self.comment_id,
            'comment' : self.comment,
            'invited_time' : self.invited_time.strftime(DATE_FORMAT),
            'commented_time' : self.commented_time.strftime(DATE_FORMAT),
	    'customer_id' : self.customer_id,
	    'expert_id' : self.expert_id,
	    'is_commented' : self.is_commented
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

if enable_search:
    whooshalchemy.whoosh_index(app, Topic)
