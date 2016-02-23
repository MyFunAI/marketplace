from config import PHOTO_BASE_DIR
from flask import Flask
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES, patch_request_class, UploadConfiguration

app = Flask(__name__)
app.config.from_object('config')
app.config.update(
    UPLOADS_DEFAULT_DEST = PHOTO_BASE_DIR
)

db = SQLAlchemy(app)
#TO-DO: 'simple' cache is not thread-safe
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

avatar_uploader = UploadSet('avatars', IMAGES)
configure_uploads(app, avatar_uploader)
patch_request_class(app, 5 * 1024 * 1024)  #Max 5M photos

from app import views, models

