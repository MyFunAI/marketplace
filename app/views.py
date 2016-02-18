from app import app
from config import *
from db_utils import *
from file_utils import *
from model_utils import *
from flask import render_template, redirect, session, url_for, request, g, jsonify, json
from .models import Customer, Expert, Topic, Category, Comment

@app.route('/')
@app.route('/index')
def index(message = 'Hello World!'):
    content = load_json_file(EXPERT_CATEGORY_PATH)
    return message

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
        #create a customer here
	if request.headers['Content-Type'] == 'application/json':
            obj = request.get_json()
	    user_id = create_user_id()
            customer = Customer(
    		user_id = user_id,
    		email = obj.get('email', ''),
    		last_seen = datetime.datetime.utcnow(),
    		name = obj.get('name', ''),
    		company = obj.get('company', ''),
    		title = obj.get('title', ''),
    		about_me = obj.get('about_me', ''),
		phone_number = obj.get('phone_number', '')
	    )
            db.session.add(customer)
            db.session.commit()
            return redirect(url_for('index', message = 'customer %d created successfully' % user_id))
        return redirect(url_for('index', message = 'content-type incorrect, customer creation failed'))
    else:
        users = Customer.query.all()
        if users is None:
            return jsonify({'customers':''})
        else:
            return jsonify({'customers':[user.serialize() for user in users]})
    return "Customer created!"

@app.route('/api/v1/experts', methods = ['POST', 'GET'])
def handle_experts():
    if request.method == 'POST':
        #create experts here
        pass
    else:
        users = Expert.query.all()
        if users is None:
            return jsonify({'experts':''})
        else:
            return jsonify({'experts':[user.serialize() for user in users]})
    return "Expert created!"


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

@app.route('/api/v1/topic/title/<topic_id>/', methods = ['GET'])
def topic_title(topic_id):
    topic = Topic.query.filter_by(topic_id = topic_id).first()
    if topic is None:
        return jsonify({'topic_id':topic_id, 'topic_title':''})
    else:
        return jsonify({'topic_id':topic_id, 'topic_title':topic.title})

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
