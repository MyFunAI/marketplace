from app import app
from config import *
from db_utils import *
from file_utils import *
from flask import render_template, session, url_for, request, g, jsonify
from .models import Customer, Expert, Topic, Category

@app.route('/')
@app.route('/index')
def index():
    content = load_json_file(EXPERT_CATEGORY_PATH)
    return "Hello, World!"

@app.route('/api/v1/customers/<customer_id>/', methods = ['GET'])
def handle_customer(customer_id):
    user = Customer.query.filter_by(user_id = customer_id).first()
    if user is None:
	return jsonify({'customers':''})
    else:
        return jsonify({'customers':[user.serialize()]})

@app.route('/api/v1/customers', methods = ['POST', 'GET'])
def handle_customers():
    if request.method == 'POST':
        #create customers here
        pass
    else:
        users = Customer.query.all()
        if users is None:
            return jsonify({'customers':''})
        else:
            return jsonify({'customers':[user.serialize() for user in users]})
    return "Customer created!"

"""
    This method loads the categories from a text file and stores it in memory.
    The key:value format of the data structure in memory is:
	category-id : ['first level category text', 'second level category text']
    The category-id is calculated by first_level_index * 100 + second_level_index
    The content of the category hierarchy is stored in a plain text file, not in db.
    Categories can only be updated (extended, modified or reduced) by the server side.
"""
@app.route('/api/v1/categories', methods = ['GET'])
def load_categories():
    #if request.method == 'POST':
    content = load_json_file(EXPERT_CATEGORY_PATH)
    categories = {}
    for i in range(len(content['level1'])):
	for j in range(len(content['level2'][i])):
	    categories[(i + 1) * CATEGORY_ID_MULTIPLIER + (j + 1)] = [content['level1'][i], content['level2'][i][j]]
	#print "current json file ", categories
    session['categories'] = categories
    return 'Categories loaded in json'

"""
	To get user 
"""
@app.route('/api/v1/user/<user_id>/', methods = ['GET'])
def user(user_id):
    user = BaseUser.query.filter_by(user_id = user_id).first()
    if user is None:
	return jsonify({'User':''})
    else:
        return jsonify({'User':user.serialize()})

"""
	To get comment 
"""
@app.route('/api/v1/comment/<comment_id>/', methods = ['GET'])
def comment(comment_id):
    comment = Comment.query.filter_by(comment_id = comment_id).first()
    if comment is None:
	return jsonify({'Comment':''})
    else:
        return jsonify({'Comment':comment.serialize()})	

"""
	To get expert 
"""
@app.route('/api/v1/expert/<expert_id>/', methods = ['GET'])
def expert(expert_id):
    user = Expert.query.filter_by(user_id = expert_id).first()
    if user is None:
	return jsonify({'Expert':''})
    else:
        return jsonify({'Expert':user.serialize()})

"""
	To get topic 
"""
@app.route('/api/v1/topic/<topic_id>/', methods = ['GET'])
def topic(topic_id):
    topic = Topic.query.filter_by(topic_id = topic_id).first()
    if topic is None:
	return jsonify({'Topic':''})
    else:
        return jsonify({'Topic':topic.serialize(topic)})

"""
	To get instruction 
"""
@app.route('/api/v1/instruction/<instruction_id>/', methods = ['GET'])
def instruction(instruction_id):
    instruction = Instruction.query.filter_by(instruction_id = instruction_id).first()
    if instruction is None:
	return jsonify({'Instruction':''})
    else:
        return jsonify({'Instruction':instruction.serialize()})

"""
	To get Category 
"""
@app.route('/api/v1/category/<category_id>/', methods = ['GET'])
def category(category_id):
    category = Category.query.filter_by(category_id = category_id).first()
    if category is None:
	return jsonify({'Category':''})
    else:
        return jsonify({'Category':category.serialize(category)})
		
@app.route('/test')
def test():
    print session['categories']
    return "Testing!"

"""
    Create some data in the db for testing purposes.
    In the command line, run:
    curl -d "" "http://localhost:5000/api/v1/internal/data/"
"""
@app.route('/api/v1/internal/data/', methods = ['POST'])
def create_data():
    create_data_in_db()
    return "Data created!"
