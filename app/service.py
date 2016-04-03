from app import cache
from config import *
from flask import Flask
from flask.ext.cache import Cache
from file_utils import *
from .models import Customer, Expert, Topic, Category, Comment, Conversation

class CustomerService:

    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_customer(cls, customer_id):
        return Customer.query.filter_by(user_id = customer_id).first()

    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_customers(cls):
	return Customer.query.all()
 
    @classmethod
    def update_customer(cls, customer_id, customer_name):
	"""
	Customer.query.filter_by
	customer = cls.load_customer(customer_id)
	customer.name = customer_name
	db.session.add(customer)
	"""

class ExpertService:

    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_expert(cls, expert_id):
        return Expert.query.filter_by(user_id = expert_id).first()

    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_experts(cls):
	return Expert.query.all()

class TopicService:

    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_topic(cls, topic_id):
        return Topic.query.filter_by(topic_id = topic_id).first()

    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_topics(cls):
	return Topic.query.all()

class TopicRequestService:

    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_request(cls, request_id):
        return TopicRequest.query.filter_by(request_id = request_id).first()

    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_requests(cls):
	return TopicRequest.query.all()

class CommentService:
    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_comment(cls, comment_id):
	return Comment.query.filter_by(comment_id = comment_id).first()

    @classmethod
    @cache.cached(timeout = CACHE_TIMEOUT)
    def load_comments(cls):
	return Comment.query.all()

class ConversationService:

    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_conversation(cls, conversation_id):
	return Conversation.query.filter_by(conversation_id = conversation_id).first()

    """
	TO-DO: time ascending order needed as well?
    """
    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_conversations(cls):
	return Conversation.query.order_by(Conversation.timestamp.desc()).all()

class CategoryService:
    @classmethod
    @cache.cached(timeout = CACHE_TIMEOUT)
    def load_categories(cls):
	return load_json_file(EXPERT_CATEGORY_PATH)

    @classmethod
    @cache.cached(timeout = CACHE_TIMEOUT)
    def load_category(cls, category_id):
	return load_json_file(EXPERT_CATEGORY_PATH)


class ImageService:
    """
	Delete old avatars a user uploaded.
	TO-DO: instead of triggering this function call every time a user uploads an avatar, a daily
	cron job could be scheduled alternatively.
    """
    @classmethod
    def delete_old_avatars(cls, user_id):
	pass

