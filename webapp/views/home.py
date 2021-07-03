from flask import Blueprint, request, render_template, redirect, jsonify, session
from webapp.models.user import User
from webapp import db

home = Blueprint('home', __name__)

# landing page
@home.route('/')
def company_homepage():
    return render_template('company-homepage.html')

@home.route('/signup')
def signup_begin():
    return render_template('begin-signup.html')

@home.route('/signup/submit-email', methods=['POST'])
def signup_submit_email():
    session['email_address'] = request.form['email_address']
    
    if User.query.filter_by(email_address=request.form['email_address']).first():
        return redirect('/signup/enter-password')
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
        if user.password == request.form['password']:
            pass # log them in
        else:
            pass # incorrect password
    else:
        user.password = request.form['password']
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
        return render_template('login-page.html')
    elif request.method == 'POST':
        pass # handle attempt to log in

