from app import app
from config import *
from file_utils import *

@app.route('/')
@app.route('/index')
def index():
    content = load_json_file(EXPERT_CATEGORY_PATH)
    return "Hello, World!"


@app.route('/test')
def test():
    return "Testing!"
