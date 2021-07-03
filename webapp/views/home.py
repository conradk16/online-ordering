from flask import Blueprint, request, render_template, redirect, jsonify

home = Blueprint('home', __name__)

# landing page
@home.route('/')
def company_homepage():
    return render_template('company-homepage.html')

# login page, also a POST endpoint for attempting to log in
@home.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login-page.html')
    elif request.method == 'POST':
        pass # handle attempt to log in

# POST endpoint for businesses to pay us - requires an HTML form and redirects them to Stripe's checkout URL
@home.route('/signup/payment', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url='https://m3orders.com/login',
            cancel_url='https://m3orders.com',
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': request.form['priceId'],
                'quantity': 1
            }],
        )
        print(checkout_session.url)
        return redirect(checkout_session.url, code=303);
    except Exception as e:
        return jsonify({'error': {'message': str(e)}}), 400
