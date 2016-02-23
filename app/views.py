from app import app, cache, avatar_uploader
from config import *
from db_utils import *
from model_utils import *
from flask import render_template, redirect, send_file, session, url_for, request, g, jsonify, json
from .models import Customer, Expert, Topic, Category, Comment
from .service import CustomerService, ExpertService, TopicService, CategoryService, CommentService
from werkzeug import secure_filename
import glob
import os

@app.route('/')
@app.route('/index')
def index(message = 'Hello World!'):
    #import pdb; pdb.set_trace()
    content = CategoryService.load_categories()
    return message

# import pdb;pdb.set_trace()
@app.route('/api/v1/customers/<customer_id>/', methods = ['GET'])
def handle_customer(customer_id):
    user = CustomerService.load_customer(customer_id)
    if user is None:
	return jsonify({})
    else:
        return jsonify({'customer' : user.serialize() })

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
        users = CustomerService.load_customers()
        if users is None:
            return jsonify({})
        else:
            return jsonify({'customers':[user.serialize() for user in users]})
    return "Customer created!"

@app.route('/api/v1/experts', methods = ['POST', 'GET'])
def handle_experts():
    if request.method == 'POST':
        #create experts here
	if request.headers['Content-Type'] == 'application/json':
            obj = request.get_json()
	    user_id = create_user_id()
	    expert = Expert(
    		user_id = user_id,
    		email = obj.get('email', ''),
    		last_seen = datetime.datetime.utcnow(),
    		name = obj.get('name', ''),
    		company = obj.get('company', ''),
    		title = obj.get('title', ''),
    		about_me = obj.get('about_me', ''),
    		degree = obj.get('degree', ''),
		university = obj.get('university', ''),
    		major = obj.get('major', ''),
    		bio = obj.get('bio', ''),
		credits = obj.get('credits', 0)
	    )
            db.session.add(expert)
            db.session.commit()
            return redirect(url_for('index', message = 'expert %d created successfully' % user_id))
        return redirect(url_for('index', message = 'content-type incorrect, expert creation failed'))
    else:
        users = ExpertService.load_experts()
        if users is None:
            return jsonify({})
        else:
            return jsonify({'experts':[user.serialize() for user in users]})
    return "Expert created!"

@app.route('/api/v1/experts/<expert_id>/', methods = ['GET'])
def handle_expert(expert_id):
    user = ExpertService.load_expert(expert_id)
    if user is None:
	return jsonify({})
    else:
        return jsonify({'expert' : user.serialize() })

"""
    This method loads the categories from a text file and stores it in memory.
    The key:value format of the data structure in memory is:
	category-id : ['first level category text', 'second level category text']
    The category-id is calculated by first_level_index * 100 + second_level_index
    The content of the category hierarchy is stored in a plain text file, not in db.
    Categories can only be updated (extended, modified or reduced) by the server side.

    TO-DO : rendering Chinese in the browser needs fixing
"""
@app.route('/api/v1/categories', methods = ['GET'])
def load_categories():
    content = CategoryService.load_categories()
    categories = {}
    for i in range(len(content['level1'])):
	for j in range(len(content['level2'][i])):
	    categories[(i + 1) * CATEGORY_ID_MULTIPLIER + (j + 1)] = [content['level1'][i], content['level2'][i][j]]
	#print "current json file ", categories
    session['categories'] = categories
    return jsonify(categories)

@app.route('/api/v1/comment/<comment_id>/', methods = ['GET'])
def handle_comment(comment_id):
    comment = CommentService.load_comment(comment_id)
    if comment is None:
	return jsonify({})
    else:
        return jsonify({'Comment' : comment.serialize()})	

@app.route('/api/v1/comments', methods = ['POST', 'GET'])
def handle_comments():
    if request.method == 'POST':
        #create comments here
	if request.headers['Content-Type'] == 'application/json':
            obj = request.get_json()
	    comment_id = obj.get('comment_id', -1)
	    comment = Comment(
    		comment_id = comment_id,
		content = obj.get('content', ''),
    		request_id = obj.get('request_id', -1),
    		rating = obj.get('rating', 0.0)
	    )
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('index', message = 'comment %d created successfully' % comment_id))
        return redirect(url_for('index', message = 'content-type incorrect, comment creation failed'))
    else:
        comments = CommentService.load_comments()
        if comments is None:
            return jsonify({})
        else:
            return jsonify({'comments' : [comment.serialize() for comment in comments]})

@app.route('/api/v1/topics', methods = ['POST', 'GET'])
def handle_topics():
    if request.method == 'POST':
        #create topics here
	if request.headers['Content-Type'] == 'application/json':
            obj = request.get_json()
	    topic_id = obj.get('topic_id', -1)
	    topic = Topic(
		topic_id = topic_id,
    		body = obj.get('body', ''),
    		title = obj.get('title', ''),
    		created_time = datetime.datetime.utcnow(),
    		rate = obj.get('rate', 0.0),
    		expert_id = obj.get('expert_id', -1)
	    )
            db.session.add(topic)
            db.session.commit()
            return redirect(url_for('index', message = 'topic %d created successfully' % topic_id))
        return redirect(url_for('index', message = 'content-type incorrect, topic creation failed'))
    else:
        topics = Topic.query.all()
        if s is None:
            return jsonify({})
        else:
            return jsonify({'topics' : [topic.serialize() for topic in topics]})

@app.route('/api/v1/topic/<topic_id>/', methods = ['GET'])
def handle_topic(topic_id):
    topic = Topic.query.filter_by(topic_id = topic_id).first()
    if topic is None:
	return jsonify({})
    else:
        return jsonify({'Topic':topic.serialize()})

"""
    The default is to rank experts in the rating-descending order.
    Rating is computed based on the ratings on all topics of an expert.

    TO-DO: add recommendation algorithms
"""
@app.route('/api/v1/recommends', methods = ['GET'])
def handle_recommends():
    experts = Expert.query.order_by(Expert.rating.desc()).all()
    if experts is None:
        return jsonify({})
    else:
	#recommendation algorithms kick in here
        return jsonify({'experts' : [expert.serialize() for expert in experts]})

"""
    Only support single avatar image uploading now.
"""
@app.route('/api/v1/avatar/<user_id>/', methods = ['POST', 'GET'])
def handle_avatar(user_id):
    if request.method == 'POST':
	if 'avatar' in request.files:
	    ext = os.path.splitext(secure_filename(request.files['avatar'].filename))
            filename = avatar_uploader.save(request.files['avatar'], str(user_id), ORIGINAL_PHOTO_FILENAME + ext[1])
            return redirect(url_for('index', message = 'avatar %s created successfully' % filename))
	else:
            return redirect(url_for('index', message = 'avatar %d not found' % user_id))
    else:
	#Find the full image path
	filenames = glob.glob(os.path.join(PHOTO_BASE_DIR, 'avatars', str(user_id), ORIGINAL_PHOTO_FILENAME + '*'))
	if len(filenames) > 0:
	    ext = os.path.splitext(filenames[0])
	    return send_file(filenames[0], mimetype = 'image/' + ext[1][1:])
	else:
            return redirect(url_for('index', message = 'avatar for %d does not exist' % user_id))

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
