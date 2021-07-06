from flask import Blueprint, request, render_template, redirect, jsonify, session
from webapp.models.user import User
from webapp import db, bcrypt
import stripe
from flask_login import login_user, logout_user, current_user

home = Blueprint('home', __name__)

# landing page
@home.route('/')
def homepage():
    return render_template('homepage.html')

# signup endpoint - signup page and requests to sign up
@home.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect('/account')
        else:
            return render_template('signup.html', user_already_exists=False)
    elif request.method == 'POST':
        user = User.query.filter_by(email_address=request.form['email_address']).first()
        if user:
            if bcrypt.check_password_hash(user.password, request.form['password']):
                if user.stripe_customer_id:
                    return redirect('/account')
                else:
                    return redirect('/signup/select-plan')
            else:
                return render_template('signup.html', user_already_exists=True)
        else:
            user = User(email_address=request.form['email_address'], password=request.form['password'])
            user.add_to_db()
            return redirect('/signup/select-plan')


@home.route('/signup/submit-email', methods=['POST'])
def signup_submit_email():
    session['email_address'] = request.form['email_address']

    user = User.query.filter_by(email_address=request.form['email_address']).first()
    if user:
        if user.password:
            return redirect('/signup/enter-password')
        else:
            return redirect('/signup/create-password')
    else:
        user = User(email_address=request.form['email_address'])
        user.add_to_db()
        return redirect('/signup/create-password')

@home.route('/signup/enter-password', methods=['GET', 'POST'])
def signup_enter_password():
    return render_template('signup-enter-password.html', email_address=session['email_address'])

@home.route('/signup/create-password')
def signup_create_password():
    return render_template('signup-create-password.html', email_address=session['email_address'])

@home.route('/signup/submit-email-password', methods=['POST'])
def signup_submit_email_password():
    user = User.query.filter_by(email_address=request.form['email_address']).first()
    if user.password:
        if bcrypt.check_password_hash(user.password, request.form['password']):
            if user.stripe_customer_id:
                return redirect('/account')
            else:
                return redirect('/signup/select-plan')
        else:
            return redirect('/signup/enter-password') # incorrect password
    else:
        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        return redirect('/signup/select-plan')

@home.route('/signup/select-plan')
def signup_select_plan():
    return render_template('signup-select-plan.html')


# POST endpoint for businesses to pay us - requires an HTML form and redirects them to Stripe's checkout URL
@home.route('/signup/payment', methods=['POST'])
def signup_payment():
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url='https://m3orders.com/login',
            cancel_url='https://m3orders.com',
            customer_email=session['email_address'],
            client_reference_id=session['email_address'],
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': request.form['price_id'],
                'quantity': 1
            }],
        )
        return redirect(checkout_session.url, code=303);
    except Exception as e:
        return jsonify({'error': {'message': str(e)}}), 400


# login page, also a POST endpoint for attempting to log in
@home.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect('/account')
        return render_template('login-page.html')
    elif request.method == 'POST':
        user = User.query.filter_by(email_address=request.form['email_address']).first()
        if user and user.password:
            if bcrypt.check_password_hash(user.password, request.form['password']):
                if user.stripe_customer_id or user.email_address == "kuklinskywork@gmail.com":
                    login_user(user, remember=True)
                    return redirect('/account')
                else:
                    return redirect('/signup/select-plan')
            else:
                return redirect('/login')
        else:
            return redirect('/login')

# logout user
@home.route('/logout')
def logout():
    logout_user()
    return redirect('/')