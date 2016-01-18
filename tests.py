#!iaskdata/bin/python
# -*- coding: utf8 -*-

from coverage import coverage
cov = coverage(branch=True, omit=['flask/*', 'tests.py'])
cov.start()

import os
import unittest
from datetime import datetime, timedelta

from config import basedir
from app import app, db
from app.models import BaseUser, Customer, Expert, Topic
#from app.translate import microsoft_translate
from tests_data import *

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')
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
	assert test_topic_1.timestamp == queried_t.timestamp

    def test_customer_no_topics(self):
        test_customer_no_topics = build_test_customer_no_topics()
        db.session.add(test_customer_no_topics)
        db.session.commit()
	queried_customer = Customer.query.get(1)
        assert queried_customer.user_id == 1
        assert queried_customer.email == 'larry@iaskdata.com'
        assert queried_customer.following_topics.all() == []
        assert queried_customer.paid_topics.all() == []

    def test_customer_topics(self):
	test_topic_1 = build_topic_1()
        test_customer_following_topics = build_customer_with_topics()
        db.session.add(test_customer_following_topics)
        test_customer_following_topics.follow_topic(test_topic_1)
        db.session.commit()
	queried_customer = Customer.query.all()
        assert queried_customer[0].user_id == 2
        assert queried_customer[0].email == 'zuck@iaskdata.com'
        assert queried_customer[0].following_topics.all() == [test_topic_1]
        assert queried_customer[0].paid_topics.all() == []

    def test_customer_multi_topics(self):
	test_topic_1 = build_topic_1()
	test_topic_2 = build_topic_2()
        test_customer_topics = build_customer_with_topics()
        db.session.add(test_customer_topics)
        test_customer_topics.follow_topic(test_topic_1)
        test_customer_topics.add_paid_topic(test_topic_2)
        db.session.commit()
	queried_customer = Customer.query.all()
        assert queried_customer[0].user_id == 2
        assert queried_customer[0].email == 'zuck@iaskdata.com'
        assert queried_customer[0].following_topics.all() == [test_topic_1]
        assert queried_customer[0].paid_topics.all() == [test_topic_2]

    """
	This has some redundancy with the test_customer_topics method above
    """
    def test_follow_topics(self):
	test_topic_1 = build_topic_1()
        test_customer_following_topics = build_customer_with_topics()
        db.session.add(test_customer_following_topics)
        db.session.commit()
        assert test_customer_following_topics.unfollow_topic(test_topic_1) is None
	t = test_customer_following_topics.follow_topic(test_topic_1)
        db.session.add(t)
        db.session.commit()
	assert test_customer_following_topics.follow_topic(test_topic_1) is None
        assert test_customer_following_topics.is_following(test_topic_1)
        assert test_customer_following_topics.following_topics.count() == 1
        assert test_customer_following_topics.following_topics.first().title == u'推荐系统求助'
        assert test_topic_1.following_customers.count() == 1
        assert test_topic_1.following_customers.first().email == 'zuck@iaskdata.com'
        t1 = test_customer_following_topics.unfollow_topic(test_topic_1)
        assert t1 is not None
        db.session.add(t1)
        db.session.commit()
        assert not t1.is_following(test_topic_1)
        assert test_customer_following_topics.following_topics.count() == 0
        assert test_topic_1.following_customers.count() == 0

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
    print "\nHTML version: " + os.path.join(basedir, "tmp/coverage/index.html")
    cov.html_report(directory='tmp/coverage')
    cov.erase()
    """
