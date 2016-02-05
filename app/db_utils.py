# -*- coding: utf8 -*-

from app import db
from file_utils import *
from .models import BaseUser, Comment, Customer, Expert, Topic, Category, Instruction

import codecs
import datetime
import json
import os

"""
    Add some comments in the database.
    Running this multiple times will incur failure due to identical primary keys.
"""
def create_comments():
    comment_1 = Comment(
        comment_id = 1,
        comment_content = 'this is one good expert!'
    )
    comment_2 = Comment(
        comment_id = 2,
        comment_content = 'this is one poor expert!'
    )
    comment_3 = Comment(
        comment_id = 3,
        comment_content = 'this is one nice expert!'
    )
    db.session.add(comment_1)
    db.session.add(comment_2)
    db.session.add(comment_3)
    db.session.commit()	

"""
    Add one user in the database.
    Running this multiple times will incur failure due to identical primary keys.
"""
def create_users():
    user_1 = BaseUser(
        user_id = 1,
        email = 'user1@gmail.com',
        last_seen = datetime.datetime.utcnow(),
        name = 'user1',
        company = 'Tsinghua University',
        title = 'Associate Prof.',
        about_me = u'this is one test',
	phone_number = '18888880001'
    )
    db.session.add(user_1)
    user_1.add_comment(Comment.query.get(1))
    user_1.add_comment(Comment.query.get(2))
    user_1.add_comment(Comment.query.get(3))
    db.session.commit()

"""
    Add some users with comments in the database.
    Running this multiple times will incur failure due to identical primary keys.
"""
def create_users_comments():
    user_1 = BaseUser(
        user_id = 2,
        email = 'user2@gmail.com',
        last_seen = datetime.datetime.utcnow(),
        name = 'user2',
        company = '2 University',
        title = 'Associate Prof.',
        about_me = u'this is one test',
	phone_number = '18888880001'
    )
    db.session.add(user_1)
    user_2 = BaseUser(
        user_id = 3,
        email = 'user3@gmail.com',
        last_seen = datetime.datetime.utcnow(),
        name = 'user3',
        company = '3 University',
        title = 'Associate Prof.',
        about_me = u'this is one test',
	phone_number = '18888880001'
    )
    db.session.add(user_2)
    user_3 = BaseUser(
        user_id = 4,
        email = 'user4@gmail.com',
        last_seen = datetime.datetime.utcnow(),
        name = 'user4',
        company = '4 University',
        title = 'Associate Prof.',
        about_me = u'this is one test',
	phone_number = '18888880001'
    )
    db.session.add(user_3)

    comment_1 = Comment(
        comment_id = 4,
        comment_content = 'this is one good expert!'
    )
    comment_2 = Comment(
        comment_id = 5,
        comment_content = 'this is one poor expert!'
    )
    db.session.add(comment_1)
    db.session.add(comment_2)
    db.session.commit()

    user_1.add_comment(Comment.query.get(4))
    user_3.add_comment(Comment.query.get(4))
    comment_1.add_user(BaseUser.query.get(2))
    comment_1.add_user(BaseUser.query.get(4))

    user_2.add_comment(Comment.query.get(5))
    user_3.add_comment(Comment.query.get(5))
    comment_2.add_user(BaseUser.query.get(3))
    comment_2.add_user(BaseUser.query.get(4))
    db.session.commit()

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
        email = 'user01@gmail.com',
        last_seen = datetime.datetime.utcnow(),
        name = 'customer01',
        company = 'Tsinghua University',
        title = 'Associate Prof.',
        about_me = u'this is one test',
	phone_number = '18888880001'
    )
    db.session.add(c1)
    c1.follow_topic(Topic.query.get(1))
    c1.follow_topic(Topic.query.get(2))
    db.session.commit()

"""
    Add one expert in the database.
    Running this multiple times will incur failure due to identical primary keys.
"""
def create_experts():
    e1 = Expert(
        user_id = 1,
        email = 'expert01@gmail.com',
        last_seen = datetime.datetime.utcnow(),
        name = 'Master A',
        company = 'Tsinghua University',
        title = 'Associate Prof.',
        about_me = u'this is one test',
    degree = 'Ph.D'
    )
    db.session.add(e1)
    e1.add_topic(Topic.query.get(2))
    e1.add_topic(Topic.query.get(3))
    db.session.commit()

"""
    Add one expert in the database.
    Running this multiple times will incur failure due to identical primary keys.
"""
def add_comment_to_expert_user():
    comment_1 = Comment(
        comment_id = 10,
        comment_content = 'this is one intersting person!'
    )
    db.session.add(comment_1)
    db.session.commit()

    bu = BaseUser.query.get(33)
    ex = Expert.query.get(3)
    bu.add_comment(Comment.query.get(10))
    ex.add_comment(Comment.query.get(10))
    comment_1.add_user(bu)
    comment_1.add_user(ex)

    db.session.commit()

"""
    Add one instruction in the database.
    Running this multiple times will incur failure due to identical primary keys.
"""
def create_instruction():
    i1 = Instruction(
        instruction_id = 1,
        header = 'register flow',
        image_url = 'register_flow.jpg'
    )
    db.session.add(i1)
    db.session.commit()

"""
    Create necessary data in the db.
    Call this method in views to populate the db with some data to play with.
"""

def create_data_in_db():

    # create_comments()
    # create_users()
    # create_users_comments()
    # create_topics()
    # create_customers()
    # create_experts()
    # create_categories()
	add_comment_to_expert_user()
    # create_instruction()
	