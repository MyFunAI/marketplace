from app import cache
from config import *
from flask import Flask
from flask.ext.cache import Cache
from file_utils import *
from .models import Customer, Expert, Topic, Category, Comment

class TimelineService:

    @classmethod
    @cache.memoize(timeout = CACHE_TIMEOUT)
    def load_hometimeline(cls, user_id, user_type, view_self):
	pass

