#!iaskdata/bin/python
# -*- coding: utf8 -*-

from datetime import datetime, timedelta
from config import basedir
from app import app, db
from app.models import BaseUser, Customer, Expert, Topic, Category, TopicRequest, Comment
from app.model_utils import *

def build_topic_1():
    test_topic_1 = Topic(
	topic_id = 1,
        body = 'Our company needs a real-time recommendation system, who can help us?',
        title = u'推荐系统求助',
        created_time = datetime.utcnow(),
        rate = 100.0,
        expert_id = 1
    )
    return test_topic_1

def build_topic_2():
    test_topic_2 = Topic(
	topic_id = 2,
        body = 'A VR company is seeking computer vision experts',
        title = u'VR & AR',
        created_time = datetime.utcnow(),
        rate = 150.0,
        expert_id = 2
    )
    return test_topic_2

def build_customer_1():
    return Customer(
        user_id = 1,
        email = 'larry@iaskdata.com',
        last_seen = datetime.utcnow(),
        name = 'larry',
        company = 'google',
        title = 'CEO',
        about_me = 'i love my job',
        phone_number = '13880089000'
    )

def build_customer_2():
    return Customer(
        user_id = 2,
        email = 'zuck@iaskdata.com',
        last_seen = datetime.utcnow(),
        name = 'zuck',
        company = 'facebook',
        title = 'CEO',
        about_me = 'i love my job',
        phone_number = '13880089001'
    )

def build_expert_1():
    return Expert(
        user_id = 3,
        email = 'andrewng@iaskdata.com',
        last_seen = datetime.utcnow(),
        name = 'Andrew NG',
        company = 'Coursera',
        title = 'Founder',
        about_me = 'I am just GOOOOD',
        degree = 'Ph.D.',
        university = 'Stanford University',
        major = 'Computer Science',
        rating = 4.9,
        profile_thumbnail_url = 'thumbnail',
        profile_image_url = 'image',
        bio = 'I graduated from the best university and I created the best company in the field',
        credits = 5
    )

def build_category_1():
    category_id = build_category_id(1, 2)
    return Category(category_id = category_id)
 
def build_category_2():
    category_id = build_category_id(1, 3)
    return Category(category_id = category_id)

def build_comment_1():
    return Comment(
        comment_id = 1,
    	content = 'this guy is really good at his major',
        request_id = 1,
        rating = 5.0
    )

def build_topic_request_1():
    return TopicRequest(
        request_id = 1,
        customer_id = 1,
        topic_id = 1,
        request_stage = 0,
    	topic_requested_time = datetime.utcnow(),
    	topic_accepted_time = datetime.utcnow(),
        topic_paid_time = datetime.utcnow(),
        topic_scheduled_time = datetime.utcnow(),
        topic_served_time = datetime.utcnow(),
        topic_rated_time = datetime.utcnow()
    )

