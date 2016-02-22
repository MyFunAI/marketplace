from app import cache
from config import *
from flask import Flask
from flask.ext.cache import Cache
from file_utils import *
from .models import Customer, Expert, Topic, Category, Comment

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
    pass

class CommentService:
    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_comment(cls, comment_id):
	return Comment.query.filter_by(comment_id = comment_id).first()

    @classmethod
    @cache.cached(timeout = CACHE_TIMEOUT)
    def load_comments(cls):
	return Comment.query.all()


class CategoryService:
    @classmethod
    @cache.cached(timeout = CACHE_TIMEOUT)
    def load_categories(cls):
	return load_json_file(EXPERT_CATEGORY_PATH)


class ImageService:
    pass

