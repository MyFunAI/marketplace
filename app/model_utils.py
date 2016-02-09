# -*- coding: utf8 -*-

from app import db
from config import *
from file_utils import *
from IDGenerator import *
from .models import BaseUser, Comment, Customer, Expert, Topic, Category, Instruction

import codecs
import datetime
import json
import os

user_id_handler = IDWorker(WORKER_ID, DATA_CENTER_ID)

"""
    We use the Twitter snowflake algorithm to generate a unique 64-bit user id.
    Our epoch begins on Jan 1, 2016

    @return
"""
def make_user_id():
    #max_user_id = db.session.query(db.func.max(User.numLogins)).scalar()
    return user_id_handler.get_id()
 
