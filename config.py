# -*- coding: utf8 -*-
import os
import pytz
import sys

"""
    These two lines are not needed in my local environment, but are needed on Heroku, hmm ...
"""
reload(sys)
sys.setdefaultencoding('utf8')

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'iaskdata.db') +
    #SQLALCHEMY_DATABASE_URI = ('mysql+mysqldb:///' + os.path.join(basedir, 'iaskdata-mysql.db') +
                               '?check_same_thread=False')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
WHOOSH_BASE = os.path.join(basedir, 'search.db')

# Whoosh does not work on Heroku
WHOOSH_ENABLED = os.environ.get('HEROKU') is None

# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

# email server
MAIL_SERVER = ''  # your mailserver
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# available languages
LANGUAGES = {
    'en': 'English',
    'es': 'Español'
}

# microsoft translation service
MS_TRANSLATOR_CLIENT_ID = ''  # enter your MS translator app id here
MS_TRANSLATOR_CLIENT_SECRET = ''  # enter your MS translator app secret here

# administrator list
ADMINS = ['you@example.com']

# pagination
POSTS_PER_PAGE = 50
MAX_SEARCH_RESULTS = 50

# Expert category file path
# EXPERT_CATEGORY_PATH = './app/resources/expert_categories.txt'
EXPERT_CATEGORY_PATH = os.path.join(basedir, 'app/resources/expert_categories.txt')
INSTRUCTION_IMAGE_PATH = '/api/v1/resources/images/instruction/'
USER_IMAGE_PATH = '/api/v1/resources/images/user/'
CATEGORY_ID_MULTIPLIER = 100

EMPTY_STRING = ''
EMPTY_DICT = {}

TIME_FORMAT = '%Y-%m-%d %H:%M:%S %f'
DATE_FORMAT = '%Y-%m-%d'

CUSTOMER_TYPE = 1
EXPERT_TYPE = 2

#EPOCH = datetime.datetime(2016, 1, 1, tzinfo = pytz.utc)
WORKER_ID = 1
DATA_CENTER_ID = 1

TOPIC_REQUESTED = 1
TOPIC_ACCEPTED = 2
TOPIC_PAID = 3
TOPIC_SCHEDULED = 4
TOPIC_SERVED = 5
TOPIC_RATED = 6
TOPIC_BAD_STAGE = 0

TOPIC_REQUESTED_MASK = 1 << (TOPIC_REQUESTED - 1)
TOPIC_ACCEPTED_MASK = 1 << (TOPIC_ACCEPTED - 1)
TOPIC_PAID_MASK = 1 << (TOPIC_PAID - 1) 
TOPIC_SCHEDULED_MASK = 1 << (TOPIC_SCHEDULED - 1)
TOPIC_SERVED_MASK = 1 << (TOPIC_SERVED - 1)
TOPIC_RATED_MASK = 1 << (TOPIC_RATED - 1)

CACHE_TIMEOUT = 120

PHOTO_BASE_DIR = '/home/guang/Documents/code/vbigdata/iaskdata-marketplace/app/resources/photos'
ORIGINAL_PHOTO_FILENAME = 'original'

