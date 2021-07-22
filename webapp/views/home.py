from flask import Blueprint, request, render_template, redirect, jsonify, session, url_for
from flask_login import login_user, logout_user, current_user
from flask_mail import Message

from webapp.models.db_models import User
from webapp import db, bcrypt, mail, env

import stripe

home = Blueprint('home', __name__)

# landing page
@home.route('/')
def homepage():
    if current_user.is_authenticated:
        return redirect('/account')
    else:
        return render_template('homepage.html')

# privacy policy
@home.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

# terms of use
@home.route('/terms-of-use')
def terms_of_use():
    return render_template('terms-of-use.html')

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

# page to request a password reset, also a POST endpoint for requesting a password reset
@home.route('/request-reset-password', methods=['GET', 'POST'])
def request_reset_password():
    if request.method == 'GET':
        return render_template('request-reset-password.html', reset_link_sent="false")
    elif request.method == 'POST':
        email = request.form['email_address']
        user = User.query.filter_by(email_address=email).first()
        send_reset_email(user)
        return render_template('request-reset-password.html', reset_link_sent="true")

# page to submit a new password, also a POST endpoint for resetting a password
@home.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        user = User.verify_reset_token(token)
        if not user:
            return redirect('/request-reset-password')
        else:
            return render_template('reset-password.html')

    elif request.method == 'POST':
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User.verify_reset_token(token)
        if not user:
            return redirect('/request-reset-password')
        else:
            user.password = password
            db.session.commit()
            return redirect('/login')

def send_reset_email(user):
    if user:
        token = user.get_reset_token()

        msg = Message(subject='M3 Orders Password Reset', sender=env['email_sender_address'], recipients=[user.email_address])
        msg.html = render_template('reset-password-email.html', reset_link=url_for('home.reset_password', token=token, _external=True))
        mail.send(msg)

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
            return redirect('/login')
        else:
            return render_template('signup-select-plan.html')
    elif request.method == 'POST':
        if (not current_user.is_authenticated) or (not is_valid_signup_select_plan_post_request(request)):
            return redirect('/login')
        else:
            session['subscription_price_id'] = request.form['subscription_price_id']
            return redirect('/signup/select-setup-fee')

@home.route('/signup/select-setup-fee', methods=['GET', 'POST'])
def signup_select_setup_fee():
    if request.method == 'GET':
        if not current_user.is_authenticated:
            return redirect('/login')
        else:
            return render_template('signup-select-fee.html')
    else:
        if not is_valid_signup_select_fee_post_request(request):
            return redirect('/login')
        else:
            try:

                shipping_address_collection = None
                line_items=[
                    {
                    'price': session['subscription_price_id'],
                    'quantity': 1
                    }]

                if request.form['setup_fee_price_id'] != '':
                    shipping_address_collection = {'allowed_countries': ['US']}
                    line_items.append({
                    'price': request.form['setup_fee_price_id'],
                    'quantity': 1
                    })


                checkout_session = stripe.checkout.Session.create(
                success_url=env['stripe_checkout_session_success_url'],
                cancel_url=env['stripe_checkout_session_cancel_url'],
                customer_email=current_user.email_address,
                client_reference_id=current_user.email_address,
                payment_method_types=['card'],
                mode='subscription',
                line_items=line_items,
                shipping_address_collection=shipping_address_collection
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
        if 'subscription_price_id' in request.form:
            return True
    return False

def is_valid_signup_select_fee_post_request(request):
    if request.form:
        if 'setup_fee_price_id' in request.form:
            if session.get('subscription_price_id'):
                return True
    return False

