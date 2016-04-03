from app import app, cache, avatar_uploader, background_image_uploader
from config import *
from db_utils import *
from exceptions import BadThings
from model_utils import *
from flask import render_template, redirect, send_file, session, url_for, request, g, jsonify, json, make_response
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, current_user
from .models import Customer, Expert, Topic, TopicRequest, Category, Comment, Conversation
from .service import *
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
"""
    Edit or retrieve a customer (POST or GET)
    @param customer_id - customer id
"""
@app.route('/api/v1/customers/<customer_id>/', methods = ['POST', 'GET'])
def handle_customer(customer_id):
    if request.method == 'POST':
        #edit an existing customer here
	if request.headers['Content-Type'] == 'application/json':
            customer = CustomerService.load_customer(customer_id)
	    if customer:
            	obj = request.get_json()
		if 'email' in obj:
    		    customer.email = obj['email']
    		if 'name' in obj:
		    customer.name = obj['name']
		if 'company' in obj:
		    customer.company = obj['company']
		if 'title' in obj:
    		    customer.title = obj['title']
    		if 'about_me' in obj:
		    customer.about_me = obj['about_me']
		if 'phone_number' in obj:
		    customer.phone_number = obj['phone_number']	
                db.session.add(customer)
                db.session.commit()
                return redirect(url_for('index', message = 'customer %d edited successfully' % customer_id))
        return redirect(url_for('index', message = 'customer %d edited successfully' % customer_id))
    else:
	#load the given customer
        user = CustomerService.load_customer(customer_id)
        if user is None:
	    return jsonify({})
        else:
            return jsonify({'customer' : user.serialize() })

"""
    Create or retrieve customers (POST or GET).
"""
@app.route('/api/v1/customers', methods = ['POST', 'GET'])
def handle_customers():
    if request.method == 'POST':
        #create a customer here
	if request.headers['Content-Type'] == 'application/json':
            obj = request.get_json()
	    for i in range(len(obj)):
   	        user_id = create_id()
                customer = Customer(
    		    user_id = user_id,
    		    email = obj[i].get('email', ''),
    		    last_seen = datetime.datetime.utcnow(),
    		    name = obj[i].get('name', ''),
    		    company = obj[i].get('company', ''),
    		    title = obj[i].get('title', ''),
    		    about_me = obj[i].get('about_me', ''),
		    phone_number = obj[i].get('phone_number', '')
	        )
                db.session.add(customer)
            db.session.commit()
            return redirect(url_for('index', message = '%d customer created successfully' % len(obj)))
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
	    for i in range(len(obj)):
  	        user_id = create_id()
	        expert = Expert(
    		    user_id = user_id,
    		    email = obj[i].get('email', ''),
    		    last_seen = datetime.datetime.utcnow(),
    		    name = obj[i].get('name', ''),
    		    company = obj[i].get('company', ''),
    		    title = obj[i].get('title', ''),
    		    about_me = obj[i].get('about_me', ''),
    		    degree = obj[i].get('degree', ''),
		    university = obj[i].get('university', ''),
    		    major = obj[i].get('major', ''),
    		    bio = obj[i].get('bio', ''),
		    credits = obj[i].get('credits', 0)
	        )
                db.session.add(expert)
            db.session.commit()
            return redirect(url_for('index', message = '%d expert created successfully' % len(obj)))
        return redirect(url_for('index', message = 'content-type incorrect, expert creation failed'))
    else:
        users = ExpertService.load_experts()
        if users is None:
            return jsonify({})
        else:
            return jsonify({'experts':[user.serialize() for user in users]})
    return "Expert created!"

"""
    Edit or retrieve expert (POST or GET)
"""
@app.route('/api/v1/experts/<expert_id>/', methods = ['POST', 'GET'])
def handle_expert(expert_id):
    if request.method == 'POST':
        #edit an existing expert here
	if request.headers['Content-Type'] == 'application/json':
            expert = ExpertService.load_expert(expert_id)
	    if expert:
            	obj = request.get_json()
		if 'email' in obj:
    		    expert.email = obj['email']
    		if 'name' in obj:
		    expert.name = obj['name']
		if 'company' in obj:
		    expert.company = obj['company']
		if 'title' in obj:
    		    expert.title = obj['title']
    		if 'about_me' in obj:
		    expert.about_me = obj['about_me']
		if 'degree' in obj:
		    expert.degree = obj['degree']
		if 'university' in obj:
		    expert.university = obj['university']
		if 'major' in obj:
		    expert.major = obj['major']
		if 'bio' in obj:
		    expert.bio = obj['bio']		
                db.session.add(expert)
                db.session.commit()
                return redirect(url_for('index', message = 'expert %d edited successfully' % expert_id))
        return redirect(url_for('index', message = 'expert %d edited successfully' % expert_id))
    else:
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

@app.route('/api/v1/comment/<comment_id>/', methods = ['POST', 'GET'])
def handle_comment(comment_id):
    if request.method == 'POST':
        #edit an existing comment here
	if request.headers['Content-Type'] == 'application/json':
    	    comment = CommentService.load_comment(comment_id)
	    if comment:
            	obj = request.get_json()
		if 'content' in obj:
		    comment.content = obj['content']
		if 'rating' in obj:
		    comment.rating = obj['rating']
                db.session.add(comment)
                db.session.commit()
                return redirect(url_for('index', message = 'comment %d edited successfully' % comment_id))
        return redirect(url_for('index', message = 'comment %d edited successfully' % comment_id))
    else:
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
	    for i in range(len(obj)):
	        comment_id = create_id()
	        comment = Comment(
    		    comment_id = comment_id,
		    content = obj[i].get('content', ''),
    		    request_id = obj[i].get('request_id', -1),
    		    rating = obj[i].get('rating', 0.0)
	        )
                db.session.add(comment)
            db.session.commit()
            return redirect(url_for('index', message = '%d comment created successfully' % len(obj)))
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
	    for i in range(len(obj)):
	        topic_id = create_id()
	        topic = Topic(
		    topic_id = topic_id,
    		    body = obj[i].get('body', ''),
    		    title = obj[i].get('title', ''),
    		    created_time = datetime.datetime.utcnow(),
    		    rate = obj[i].get('rate', 0.0),
    		    expert_id = obj[i].get('expert_id', -1)
	        )
                db.session.add(topic)
            db.session.commit()
            return redirect(url_for('index', message = '%d topic created successfully' % len(obj)))
        return redirect(url_for('index', message = 'content-type incorrect, topic creation failed'))
    else:
        topics = TopicService.load_topics()
        if topics is None:
            return jsonify({})
        else:
            return jsonify({'topics' : [topic.serialize() for topic in topics]})

"""
    Edit or retrieve a topic (POST or GET)
"""
@app.route('/api/v1/topic/<topic_id>/', methods = ['POST', 'GET'])
def handle_topic(topic_id):
    if request.method == 'POST':
        #edit an existing topic here
	if request.headers['Content-Type'] == 'application/json':
    	    topic = TopicService.load_topic(topic_id)
	    if topic:
            	obj = request.get_json()
		if 'body' in obj:
		    topic.body = obj['body']
		if 'title' in obj:
		    topic.title = obj['title']
                db.session.add(topic)
                db.session.commit()
                return redirect(url_for('index', message = 'topic %d edited successfully' % topic_id))
        return redirect(url_for('index', message = 'topic %d edited successfully' % topic_id))
    else:
    	topic = TopicService.load_topic(topic_id)
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
	    for i in range(len(obj)):
    	        request_id = create_id()
	        r = TopicRequest(
	            request_id = request_id,
    	            customer_id = obj[i].get('customer_id', -1),
		    topic_id = obj[i].get('topic_id', -1),
		    request_stage = obj[i].get('request_stage', 1),
    		    topic_requested_time = datetime.datetime.utcnow()
	        )
	        db.session.add(r)
	    db.session.commit()
            return redirect(url_for('index', message = '%d topic request created successfully' % len(obj)))
        return redirect(url_for('index', message = 'content-type incorrect, topic request creation failed'))
    else:
        requests = TopicRequestService.load_requests()
        if requests is None:
            return jsonify({})
        else:
            return jsonify({'topic_requests' : [r.serialize() for r in requests]})

"""
    Edit or retrieve a request (POST or GET)
    Editing a request essentially means canceling a request.
    TO-DO: which side can cancel a request and at what stage can a cancellation happen
"""
@app.route('/api/v1/request/<request_id>/', methods = ['POST', 'GET'])
def handle_request(request_id):
    if request.method == 'POST':
        #edit an existing topic request here
    	topic_request = TopicRequestService.load_request(request_id)
	if topic_request:
	    u = g.user.remove_topic_request_by_request(topic_request)
	    if u:
                db.session.add(u)
                db.session.commit()
                return redirect(url_for('index', message = 'topic request %d cancled successfully' % request_id))
        return redirect(url_for('index', message = 'topic request %d canceled unsuccessfully' % request_id))
    else:
    	topic_request = TopicRequestService.load_request(request_id)
        if topic_request is None:
	    return jsonify({})
        else:
            return jsonify({'topic_request':topic_request.serialize()})

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
        convs = ConversationService.load_conversations()
        if convs is None:
            return jsonify({})
        else:
            return jsonify({'conversations' : [c.serialize() for c in convs]})

"""
    TO-DO: recall a recent conversation like what WeChat does
"""
@app.route('/api/v1/conversation/<conversation_id>/', methods = ['GET'])
def handle_conversation(conversation_id):
    conv = ConversationService.load_conversation(conversation_id)
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

@app.route('/api/v1/background_image/<user_id>/', methods = ['POST', 'GET'])
def handle_background_image(user_id):
    if request.method == 'POST':
	if 'background_image' in request.files and 'user_type' in request.form:
	    if request.form['user_type'] == 'customer':
		#Customers
		user = CustomerService.load_customer(user_id)
	    else:
		#Experts 
		user = ExpertService.load_expert(user_id)
	    if user:
	        ext = os.path.splitext(secure_filename(request.files['background_image'].filename))
                filename = background_image_uploader.save(request.files['background_image'], str(user_id), ORIGINAL_PHOTO_FILENAME + ext[1])
	        full_path = os.path.join('backgrounds', filename)
		user.background_image_url = full_path
		db.session.flush()
                db.session.commit()
                return redirect(url_for('index', message = 'background image %s created successfully' % filename))
	    else:
	        raise BadThings('User not found', status_code = 404)
	else:
	    msg = ''
	    if 'background_image' not in request.files:
		msg = 'background image not provided in request'
	    if 'user_type' not in request.form:
		msg += ', user type missing in request'
	    raise BadThings(msg, status_code = 400)
    else:
	#Find the full image path
	filenames = glob.glob(os.path.join(PHOTO_BASE_DIR, 'backgrounds', str(user_id), ORIGINAL_PHOTO_FILENAME + '*'))
	if len(filenames) > 0:
	    ext = os.path.splitext(filenames[0])
	    return send_file(filenames[0], mimetype = 'image/' + ext[1][1:])
	else:
	    raise BadThings('Background image not found on server', status_code = 410)

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
		user = CustomerService.load_customer(user_id)
	    else:
		#Experts 
		user = ExpertService.load_expert(user_id)
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

