from flask import Blueprint, request, render_template, redirect, jsonify, session, url_for
from flask_login import login_user, logout_user, current_user

from webapp.models.user import User
from webapp import db, bcrypt

import stripe

home = Blueprint('home', __name__)

# landing page
@home.route('/')
def homepage():
    return render_template('homepage.html')

# login page, also a POST endpoint for attempting to log in
@home.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect('/account')
        else:
            if 'invalid_credentials' in session:
                invalid_credentials = session['invalid_credentials']
            else:
                invalid_credentials = "false"
            session['invalid_credentials'] = "false"
            return render_template('login.html', invalid_credentials=invalid_credentials)
    elif request.method == 'POST':
        if not is_valid_login_post_request(request):
            session['invalid_credentials'] = "true"
            return redirect(url_for('home.login_page'))
        
        user = User.query.filter_by(email_address=request.form['email_address']).first()
        if user and user.password:
            if bcrypt.check_password_hash(user.password, request.form['password']):
                if 'remember_me' in request.form:
                    login_user(user, remember=True)
                else:
                    login_user(user, remember=False)
                if user.stripe_customer_id:
                    return redirect('/account')
                else:
                    return redirect('/signup/select-plan')
            else:
                session['invalid_credentials'] = "true"
                return redirect(url_for('home.login_page'))
        else:
            session['invalid_credentials'] = "true"
            return redirect(url_for('home.login_page'))

# logout POST endpoint
@home.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# signup page, also a POST endpoint for signing up
@home.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect('/account')
        else:
            return render_template('signup.html', user_already_exists="false")
    elif request.method == 'POST':
        if not is_valid_signup_post_request(request):
            return redirect('/signup')

        user = User.query.filter_by(email_address=request.form['email_address']).first()
        if user:
            if bcrypt.check_password_hash(user.password, request.form['password']):
                login_user(user, remember=False)
                if user.stripe_customer_id:
                    return redirect('/account')
                else:
                    return redirect('/signup/select-plan')
            else:
                return render_template('signup.html', user_already_exists="true")
        else:
            user = User(email_address=request.form['email_address'], password=bcrypt.generate_password_hash(request.form['password']).decode('utf-8'))
            user.add_to_db()
            login_user(user, remember=False)
            return redirect('/signup/select-plan')

# select plan page, also a POST endpoint for choosing a plan and being redirected to Stripe checkout
@home.route('/signup/select-plan', methods=['GET', 'POST'])
def signup_select_plan():
    if request.method == 'GET':
        if not current_user.is_authenticated:
            return redirect(url_for('home.login_page'))
        else:
            return render_template('signup-select-plan.html')
    elif request.method == 'POST':
        if (not current_user.is_authenticated) or (not is_valid_signup_select_plan_post_request(request)):
            return redirect(url_for('home.login_page'))
        else:
            try:
                checkout_session = stripe.checkout.Session.create(
                success_url='https://m3orders.com/login',
                cancel_url='https://m3orders.com',
                customer_email=current_user.email_address,
                client_reference_id=current_user.email_address,
                payment_method_types=['card'],
                mode='subscription',
                line_items=[{
                    'price': request.form['price_id'],
                    'quantity': 1
                }]
            )
                return redirect(checkout_session.url, code=303);
            except Exception as e:
                return jsonify({'error': {'message': str(e)}}), 400

def is_valid_login_post_request(request):
    if request.form:
        if ('email_address' in request.form) and ('password' in request.form):
            if (len(request.form['email_address']) <= 100) and (len(request.form['email_address']) > 0) and (len(request.form['password']) <= 100) and (len(request.form['password']) > 0):
                return True
    return False

def is_valid_signup_post_request(request):
    if request.form:
        if ('email_address' in request.form) and ('password' in request.form):
            if (len(request.form['email_address']) <= 100) and (len(request.form['email_address']) > 0) and (len(request.form['password']) <= 100) and (len(request.form['password']) > 0):
                return True
    return False

def is_valid_signup_select_plan_post_request(request):
    if request.form:
        if 'price_id' in request.form:
            return True
    return False


