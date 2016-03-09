# -*- coding: utf8 -*-

#from app import db
from config import *
from file_utils import *
from IDGenerator import *
#from .models import BaseUser, Comment, Customer, Expert, Topic, Category, Instruction

import codecs
import json
import os

id_handler = IDWorker(WORKER_ID, DATA_CENTER_ID)

"""
    We use the Twitter snowflake algorithm to generate a unique 64-bit user id.
    Our epoch begins on Jan 1, 2016

    @return
"""
def create_id():
    return id_handler.get_id()

def build_category_id(first_level_index, second_level_index):
    return first_level_index * 100 + second_level_index

def get_first_level_category_index(category_id):
    return category_id / 100

def get_second_level_category_index(category_id):
    return category_id % 100

