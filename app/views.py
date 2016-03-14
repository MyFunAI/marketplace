from app import app, cache, avatar_uploader
from config import *
from db_utils import *
from exceptions import BadThings
from model_utils import *
from flask import render_template, redirect, send_file, session, url_for, request, g, jsonify, json, make_response
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, current_user
from .models import Customer, Expert, Topic, TopicRequest, Category, Comment, Conversation
from .service import CustomerService, ExpertService, TopicService, CategoryService, CommentService
from .oauth_service import *
from .timeline_service import *
from werkzeug import secure_filename
import glob
import os

@app.before_request
def before_request():
    g.user = current_user
    """
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = get_locale()
    """

@app.route('/')
@app.route('/index')
def index(message = 'Hello World!'):
    #import pdb; pdb.set_trace()
    content = CategoryService.load_categories()
    return message

"""
@app.route('/user_info')
def get_user_info():
    if 'qq_token' in session:
        data = update_qq_api_request_data()
        resp = qq.get('/user/get_user_info', data=data)
        return jsonify(status=resp.status, data=resp.data)
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return qq.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('qq_token', None)
    return redirect(url_for('get_user_info'))

@app.route('/login/authorized')
def authorized():
    resp = qq.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['qq_token'] = (resp['access_token'], '')

    # Get openid via access_token, openid and access_token are needed for API calls
    resp = qq.get('/oauth2.0/me', {'access_token': session['qq_token'][0]})
    resp = json_to_dict(resp.data)
    if isinstance(resp, dict):
        session['qq_openid'] = resp.get('openid')

    return redirect(url_for('get_user_info'))


@qq.tokengetter
def get_qq_oauth_token():
    return session.get('qq_token')
"""

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
	    user_id = create_id()
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

"""
    This endpoint only handles basic fields of an expert class, and that is what actually happens when
    an expert is onboard.
    Other complex fields of expert class such as TopicRequests are not added by this endpoint.
"""
@app.route('/api/v1/experts', methods = ['POST', 'GET'])
def handle_experts():
    if request.method == 'POST':
        #create experts here
	if request.headers['Content-Type'] == 'application/json':
            obj = request.get_json()
	    user_id = create_id()
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
	    comment_id = create_id()
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
	    topic_id = create_id()
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
        if topics is None:
            return jsonify({})
        else:
            return jsonify({'topics' : [topic.serialize() for topic in topics]})

@app.route('/api/v1/topic/<topic_id>/', methods = ['GET'])
def handle_topic(topic_id):
    topic = Topic.query.filter_by(topic_id = topic_id).first()
    if topic is None:
	return jsonify({})
    else:
        return jsonify({'topic':topic.serialize()})

@app.route('/api/v1/requests', methods = ['POST', 'GET'])
def handle_requests():
    if request.method == 'POST':
        #create topic request here
	if request.headers['Content-Type'] == 'application/json':
            obj = request.get_json()
    	    request_id = create_id()
	    r = TopicRequest(
	        request_id = request_id,
    	        customer_id = obj.get('customer_id', -1),
		topic_id = obj.get('topic_id', -1),
		request_stage = obj.get('request_stage', 1),
    		topic_requested_time = datetime.datetime.utcnow()
	    )
	    db.session.add(r)
	    db.session.commit()
            return redirect(url_for('index', message = 'topic request %d created successfully' % request_id))
        return redirect(url_for('index', message = 'content-type incorrect, topic request creation failed'))
    else:
        requests = TopicRequest.query.all()
        if requests is None:
            return jsonify({})
        else:
            return jsonify({'topic_requests' : [r.serialize() for r in requests]})

@app.route('/api/v1/request/<request_id>/', methods = ['GET'])
def handle_request(request_id):
    request = TopicRequest.query.filter_by(request_id = request_id).first()
    if request is None:
	return jsonify({})
    else:
        return jsonify({'topic_request':request.serialize()})

@app.route('/api/v1/conversations', methods = ['POST', 'GET'])
def handle_conversations():
    if request.method == 'POST':
	if request.headers['Content-Type'] == 'application/json':
            obj = request.get_json()
	    for i in range(len(obj)):
	        conv_id = create_id()
	        c = Conversation(
    		    conversation_id = conv_id,
    		    message = obj[i].get('message', 'no message'),
		    request_id = obj[i].get('request_id', -1),
		    user_1_id = obj[i].get('user_1_id', -1),
		    user_2_id = obj[i].get('user_2_id', -1),
    		    timestamp = datetime.datetime.utcnow()
	        )
	        db.session.add(c)
	    db.session.commit()
            return redirect(url_for('index', message = '%d conversations created successfully' % len(obj)))
        return redirect(url_for('index', message = 'content-type incorrect, conversation creation failed'))
    else:
        convs = Conversation.query.order_by(Conversation.timestamp.desc()).all()
        if convs is None:
            return jsonify({})
        else:
            return jsonify({'conversations' : [c.serialize() for c in convs]})

@app.route('/api/v1/conversation/<conversation_id>/', methods = ['GET'])
def handle_conversation(conversation_id):
    conv = Conversation.query.filter_by(conversation_id = conversation_id).first()
    if conv is None:
	return jsonify({})
    else:
        return jsonify({'conversation' : conv.serialize()})

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
    For the POST mode, another argument indicating the type of users is needed. The Customer/Expert db is updated
    as well, i.e., the 'avatar_url' field is updated.

    TO-DO: crop the raw avatar to generate a thumbnail 
"""
@app.route('/api/v1/avatar/<user_id>/', methods = ['POST', 'GET'])
def handle_avatar(user_id):
    if request.method == 'POST':
	if 'avatar' in request.files and 'user_type' in request.form:
	    if request.form['user_type'] == 'customer':
		#Customers
		user = Customer.query.filter_by(user_id = user_id).first()
	    else:
		#Experts 
		user = Expert.query.filter_by(user_id = user_id).first()
	    if user:
	        ext = os.path.splitext(secure_filename(request.files['avatar'].filename))
                filename = avatar_uploader.save(request.files['avatar'], str(user_id), ORIGINAL_PHOTO_FILENAME + ext[1])
	        full_path = os.path.join('avatars', filename)
		user.avatar_url = full_path
		db.session.flush()
                db.session.commit()
	        #avatar saved, filename =  17526161080979456/original.jpg
                return redirect(url_for('index', message = 'avatar %s created successfully' % filename))
	    else:
	        raise BadThings('User not found', status_code = 404)
	else:
	    msg = ''
	    if 'avatar' not in request.files:
		msg = 'avatar image not provided in request'
	    if 'user_type' not in request.form:
		msg += ', user type missing in request'
	    raise BadThings(msg, status_code = 400)
    else:
	#Find the full image path
	filenames = glob.glob(os.path.join(PHOTO_BASE_DIR, 'avatars', str(user_id), ORIGINAL_PHOTO_FILENAME + '*'))
	if len(filenames) > 0:
	    ext = os.path.splitext(filenames[0])
	    return send_file(filenames[0], mimetype = 'image/' + ext[1][1:])
	else:
	    raise BadThings('Avatar not found on server', status_code = 410)

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

"""
    A customer shows interests on an expert.
    TO-DO: handle login-required issues.
    @param user_id - user id of an expert
"""
@app.route('/interestedins/<int:user_id>', methods = ['POST', 'GET', 'DELETE'])
def follow(user_id):
    user = Expert.query.filter_by(user_id = user_id).first()
    if user is None:
	raise BadThings('Target expert not found', status_code = 404)
    if request.method == 'POST':
        if user == g.user:
   	    raise BadThings('Cannot follow yourself', status_code = 400)
        u = g.user.follow_expert(user)
        if u is None:
            return BadThings('Cannot follow expert %d' % user_id, status_code = 400)
        db.session.add(u)
        db.session.commit()
        return make_response(jsonify({'message': 'following expert %d successfully' % user_id}), 200)
    elif request.method == 'GET':
	if g.user.is_following_expert(user):
	    msg = 'Following target expert %d' % user_id 
	else:
	    msg = 'Not following target expert %d' % user_id
        return make_response(jsonify({'message': msg}), 200)
    elif request.method == 'DELETE':
	#delete the interested-in relationship, i.e., the customer unfollows the expert
	u = g.user.unfollow_expert(user)
        if u is None:
            return BadThings('Cannot unfollow expert %d' % user_id, status_code = 400)
        db.session.add(u)
        db.session.commit()
        return make_response(jsonify({'message': 'unfollowing expert %d successfully' % user_id}), 200)
    else:
        return make_response(jsonify({'message': 'ACTION not supported'}), 403)

@app.route('/hometimeline/<int:user_id>', methods = ['GET'])
def get_hometimeline(user_id):
    user = Expert.query.filter_by(user_id = user_id).first()
    home_timeline = TimelineService.load_hometimeline()
    return jsonify({'home_timeline' : home_timeline})

@app.route("/login/<user>/<password>")
def test_login(user, password):
    return "user : %s password : %s" % (user, password)
	
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

@app.errorhandler(BadThings)
def handle_missing_resource(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

