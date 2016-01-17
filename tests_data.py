#!iaskdata/bin/python
# -*- coding: utf8 -*-

from datetime import datetime, timedelta
from config import basedir
from app import app, db
from app.models import BaseUser, Customer, Expert, Topic

test_topic_1 = Topic(
	topic_id = 1,
        body = 'Our company needs a real-time recommendation system, who can help us?',
        title = u'推荐系统求助',
        timestamp = datetime.utcnow(),
        rate = 100.0,
        expert_id = 1
)

test_topic_2 = Topic(
	topic_id = 2,
        body = 'A VR company is seeking computer vision experts',
        title = u'VR & AR',
        timestamp = datetime.utcnow(),
        rate = 150.0,
        expert_id = 2
)

test_customer_no_topics = Customer(
        user_id = 1,
        email = 'larry@iaskdata.com',
        last_seen = datetime.utcnow(),
        name = 'larry',
        company = 'google',
        title = 'CEO',
        about_me = 'i love my job',
        phone_number = '13880089000'
)

test_customer_following_topics = Customer(
        user_id = 2,
        email = 'zuck@iaskdata.com',
        last_seen = datetime.utcnow(),
        name = 'zuck',
        company = 'facebook',
        title = 'CEO',
        about_me = 'i love my job',
        phone_number = '13880089001'
)
test_customer_following_topics.follow_topic(test_topic_1)

test_customer_following_and_paying_topics = Customer(
        user_id = 3,
        email = 'tim@iaskdata.com',
        last_seen = datetime.utcnow(),
        name = 'tim',
        company = 'apple',
        title = 'CEO',
        about_me = 'i love my job',
        phone_number = '13880089002'
)
