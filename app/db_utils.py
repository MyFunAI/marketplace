# -*- coding: utf8 -*-

from app import db
from file_utils import *
from .models import Customer, Expert, Topic, Category

import codecs
import datetime
import json
import os

"""
    Add some topics in the database.
    Running this multiple times will incur failure due to identical primary keys.
"""
def create_topics():
    topic_1 = Topic(
        topic_id = 1,
        body = 'I am a scientist at Facebook, where I lead the News Feed recommendation team',
        title = u'从0到1搭建推荐系统',
        timestamp = datetime.datetime.utcnow(),
        rate = 200.0,
        expert_id = 1
    )
    topic_2 = Topic(
        topic_id = 2,
        body = 'I worked on recommendation algorithms and systems at Google and LinkedIn.',
        title = u'Machine Learning in Practice',
        timestamp = datetime.datetime.utcnow(),
        rate = 100.0,
        expert_id = 1
    )
    topic_3 = Topic(
        topic_id = 3,
        body = 'Computer vision on the move. I have been working on CV for 10 years and I am now the CTO of a unicorn in SV',
        title = u'Computer vision algorithms in reality',
        timestamp = datetime.datetime.utcnow(),
        rate = 150.0,
        expert_id = 2
    )
    db.session.add(topic_1)
    db.session.add(topic_2)
    db.session.add(topic_3)
    db.session.commit()

#def create_categories():

"""
    Prior to running this, we need to make sure that topics exist in db. In other words,
    create_topics() should be run first. 
"""
def create_customers():
    """
    c1 = Customer(
        user_id = 1,
        email = 'user01@gmail.com',
        last_seen = datetime.datetime.utcnow(),
        name = 'customer01',
        company = 'Tsinghua University',
        title = 'Associate Prof.',
        about_me = u'机器学习副教授，我也在搞大数据项目',
	phone_number = '18888880001'
    )
    db.session.add(c1)
    c1.follow_topic(Topic.query.get(1))
    c1.follow_topic(Topic.query.get(2))
    db.session.commit()
    """

    c1 = Customer(
        user_id = 2,
        email = 'user02@gmail.com',
        last_seen = datetime.datetime.utcnow(),
        name = 'customer02',
        company = 'Tencent',
        title = 'Engineering Director',
        about_me = u'Seeking algorithm talents for our 大数据 projects',
	phone_number = '18888880002'
    )
    db.session.add(c1)
    c1.follow_topic(Topic.query.get(1))
    db.session.commit()

"""
    Create necessary data in the db.
    Call this method in views to populate the db with some data to play with.
"""
def create_data_in_db():
    #create_topics()
    create_customers()

