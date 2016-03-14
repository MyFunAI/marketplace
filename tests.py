#!iaskdata/bin/python
# -*- coding: utf8 -*-

from coverage import coverage
cov = coverage(branch=True, omit=['flask/*', 'tests.py'])
cov.start()

import os
import unittest
from datetime import datetime, timedelta

from config import BASEDIR
from app import app, db
#from app.models import BaseUser, Customer, Expert, Topic, TopicRequest, Comment
#from app.translate import microsoft_translate
from tests_data import *

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(BASEDIR, 'test.db')
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_topic(self):
	test_topic_1 = build_topic_1()
        db.session.add(test_topic_1)
        db.session.commit()
        queried_t = Topic.query.get(1)
	assert test_topic_1.topic_id == 1
	assert test_topic_1.title == '推荐系统求助'
	assert test_topic_1.rate == 100.0
	assert test_topic_1.created_time == queried_t.created_time
	assert test_topic_1.expert_id == 101
	assert test_topic_1.body == 'Our company needs a real-time recommendation system, who can help us?'

    def test_customer_no_topics(self):
        test_customer_1 = build_customer_1()
        db.session.add(test_customer_1)
        db.session.commit()
	queried_customer = Customer.query.get(1)
        assert queried_customer.user_id == 1
        assert queried_customer.email == 'larry@iaskdata.com'
        assert queried_customer.topic_requests.all() == []

    def test_customer_with_ongoing_topics(self):
	test_topic_1 = build_topic_1()
	test_topic_2 = build_topic_2()
        test_customer_1 = build_customer_1()
        db.session.add(test_customer_1)
        db.session.commit()
        assert test_customer_1.is_topic_being_requested(test_topic_1) is False
        assert test_customer_1.add_topic_request(test_topic_1)
        assert test_customer_1.is_topic_being_requested(test_topic_1) is True
        assert test_customer_1.add_topic_request(test_topic_1) is None
	assert test_customer_1.remove_topic_request(test_topic_1)
        assert test_customer_1.is_topic_being_requested(test_topic_1) is False
	assert test_customer_1.remove_topic_request(test_topic_2) is None
        assert test_customer_1.is_topic_being_requested(test_topic_2) is False
        assert test_customer_1.add_topic_request(test_topic_2)
	queried_customer = Customer.query.get(1)
        assert queried_customer.user_id == 1
        assert queried_customer.email == 'larry@iaskdata.com'
        assert queried_customer.topic_requests.first().topic == test_topic_2

    def test_customer_complete_topics(self):
	test_topic_1 = build_topic_1()
	test_topic_2 = build_topic_2()
        test_customer_1 = build_customer_1()
        db.session.add(test_customer_1)
        assert test_customer_1.add_topic_request(test_topic_1)
        assert test_customer_1.add_topic_request(test_topic_2)
        db.session.commit()
	requests = test_customer_1.get_ongoing_requests_by_topic(test_topic_1)
	assert len(requests) == 1
	assert requests[0].topic_id == test_topic_1.topic_id
        assert [t.topic for t in test_customer_1.topic_requests.all()] == [test_topic_1, test_topic_2]
	assert len(test_customer_1.get_ongoing_requests()) == 2
	requests[0].set_to_completed()
	requests = test_customer_1.get_ongoing_requests()
	assert len(requests) == 1
	assert requests[0].topic_id == test_topic_2.topic_id

    def test_experts(self):
	test_topic_1 = build_topic_1()
	test_expert = build_expert_1()
        test_customer_1 = build_customer_1()
        test_customer_2 = build_customer_2()
        db.session.add(test_expert)
        db.session.add(test_customer_1)
        db.session.add(test_customer_2)
        db.session.commit()
	assert test_expert.get_followee_count() == 0
	assert test_expert.get_follower_count() == 0
	test_customer_1.follow_expert(test_expert)
	assert test_expert.get_follower_count() == 1
	test_customer_2.follow_expert(test_expert)
	assert test_expert.get_follower_count() == 2
	assert test_expert.remove_topic(test_topic_1) is None
	t = test_expert.add_topic(test_topic_1)
	assert test_expert.user_id == 101
	assert test_expert.email == 'andrewng@iaskdata.com'
	assert test_expert.name == 'Andrew NG'
        assert test_expert.company == 'Coursera'
        assert test_expert.title == 'Founder'
        assert test_expert.about_me == 'I am just GOOOOD'
	assert test_expert.degree == 'Ph.D.'
        assert test_expert.university == 'Stanford University'
	assert test_expert.major == 'Computer Science'
	assert test_expert.rating == 4.9
	assert len(test_expert.serving_topics) == 1
	assert test_expert.serving_topics[0].expert_id == 101
	assert test_expert.serving_topics[0].title == u'推荐系统求助'
        assert test_expert.serving_topics[0].rate == 100.0
	assert test_expert.remove_topic(test_topic_1)
	assert not test_expert.has_topic(test_topic_1)
	assert len(test_expert.serving_topics) == 0

    def test_category(self):
	test_expert = build_expert_1()
        db.session.add(test_expert)
        db.session.commit()
	test_category_1 = build_category_1()
	assert test_expert.remove_tag(test_category_1) is None
	t = test_expert.add_tag(test_category_1)
	assert len(test_expert.tags) == 1
	assert test_expert.tags[0].category_id == 102 
	assert test_expert.has_tag(test_category_1)
	test_category_2 = build_category_2()
	t = test_expert.add_tag(test_category_2)
	assert len(test_expert.tags) == 2
	assert test_expert.tags[1].category_id == 103

    def test_average_topic_rating(self):
	test_topic_request_1 = build_topic_request_1()
	test_topic_request_2 = build_topic_request_2()
	test_comment_1 = build_comment_1()
	test_comment_2 = build_comment_2()
	test_topic_1 = build_topic_1()
	test_expert = build_expert_1()
        db.session.add(test_expert)
	db.session.commit()
	test_topic_request_1.topic = test_topic_1
	test_topic_request_2.topic = test_topic_1
	test_topic_request_1.comment = test_comment_1
	test_topic_request_2.comment = test_comment_2 
	assert len(test_expert.serving_topics) == 0
	test_expert.add_topic(test_topic_1)
	assert len(test_expert.serving_topics) == 1
	assert len(test_topic_1.get_ongoing_requests()) == 2
	assert test_topic_1.compute_rating() == 0.0
	test_topic_request_1.set_to_rated()
	assert len(test_topic_1.get_ongoing_requests()) == 1
	assert len(test_topic_1.get_completed_requests()) == 1
	assert test_topic_1.compute_rating() == 4.6
	test_topic_request_2.set_to_rated()
	assert len(test_topic_1.get_ongoing_requests()) == 0
	assert len(test_topic_1.get_completed_requests()) == 2
	assert round(test_topic_1.compute_rating(), 2) == 4.70
 
    """
    @unittest.skip("Not being tested for the moment")
    def test_avatar(self):
        # create a user
        u = User(nickname='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/' + \
            'd4c74594d841139328695756648b6bd6'
        assert avatar[0:len(expected)] == expected

    @unittest.skip("Not being tested for the moment")
    def test_follow_posts(self):
        # make four users
        u1 = User(nickname='john', email='john@example.com')
        u2 = User(nickname='susan', email='susan@example.com')
        u3 = User(nickname='mary', email='mary@example.com')
        u4 = User(nickname='david', email='david@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        # make four posts
        utcnow = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  timestamp=utcnow + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  timestamp=utcnow + timedelta(seconds=2))
        p3 = Post(body="post from mary", author=u3,
                  timestamp=utcnow + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  timestamp=utcnow + timedelta(seconds=4))
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.commit()
        # setup the followers
        u1.follow(u1)  # john follows himself
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u2)  # susan follows herself
        u2.follow(u3)  # susan follows mary
        u3.follow(u3)  # mary follows herself
        u3.follow(u4)  # mary follows david
        u4.follow(u4)  # david follows himself
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()
        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        assert len(f1) == 3
        assert len(f2) == 2
        assert len(f3) == 2
        assert len(f4) == 1
        assert f1[0].id == p4.id
        assert f1[1].id == p2.id
        assert f1[2].id == p1.id
        assert f2[0].id == p3.id
        assert f2[1].id == p2.id
        assert f3[0].id == p4.id
        assert f3[1].id == p3.id
        assert f4[0].id == p4.id

    @unittest.skip("Not being tested for the moment")
    def test_delete_post(self):
        # create a user and a post
        u = User(nickname='john', email='john@example.com')
        p = Post(body='test post', author=u, timestamp=datetime.utcnow())
        db.session.add(u)
        db.session.add(p)
        db.session.commit()
        # query the post and destroy the session
        p = Post.query.get(1)
        db.session.remove()
        # delete the post using a new session
        db.session = db.create_scoped_session()
        db.session.delete(p)
        db.session.commit()

    @unittest.skip("Not being tested for the moment")
    def test_translation(self):
        assert microsoft_translate(u'English', 'en', 'es') == u'Inglés'
        assert microsoft_translate(u'Español', 'es', 'en') == u'Spanish'
    """

if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    """
    cov.stop()
    cov.save()
    print "\n\nCoverage Report:\n"
    cov.report()
    print "\nHTML version: " + os.path.join(BASEDIR, "tmp/coverage/index.html")
    cov.html_report(directory='tmp/coverage')
    cov.erase()
    """
