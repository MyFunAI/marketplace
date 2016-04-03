from config import PHOTO_BASE_DIR, QQ_APP_ID, QQ_APP_KEY
from flask import Flask
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES, patch_request_class, UploadConfiguration
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config.from_object('config')
app.config.update(
    UPLOADS_DEFAULT_DEST = PHOTO_BASE_DIR
)
app.config['OAUTH_CREDENTIALS'] = {
    'qq': {
	#qq open platform uses 'key' instead of 'secret'
        'id': '1105136607',
        'secret': 'd9EKBHt0jYVJJn9v'
    },
    'wechat': {
        'id': '',
        'secret': ''
    }
}

app.secret_key = 'development'
oauth = OAuth(app)

qq = oauth.remote_app(
    'qq',
    consumer_key = QQ_APP_ID,
    consumer_secret = QQ_APP_KEY,
    base_url = 'https://graph.qq.com',
    request_token_url = None,
    request_token_params= {'scope' : 'get_user_info'},
    access_token_url = '/oauth2.0/token',
    authorize_url = '/oauth2.0/authorize',
)

db = SQLAlchemy(app)
#TO-DO: 'simple' cache is not thread-safe
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

avatar_uploader = UploadSet('avatars', IMAGES)
configure_uploads(app, avatar_uploader)
patch_request_class(app, 5 * 1024 * 1024)  #Max 5M photos

background_image_uploader = UploadSet('backgrounds', IMAGES)
configure_uploads(app, background_image_uploader)

from app import views, models

