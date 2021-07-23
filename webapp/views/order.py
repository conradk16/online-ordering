from flask import Blueprint, render_template, request, jsonify, session, redirect
from webapp.models.order import *
from webapp.models.db_models import User, Order
from webapp import db, env
import stripe
import json
import datetime
from webapp.views.account import calculate_next_closing_time

order = Blueprint('order', __name__)

@order.route('/super-cucas-micheltorena', methods=['GET', 'POST'])
def super_cucas_micheltorena():
    return handle_order_website_request(request, 'test@gmail.com', '/super-cucas-micheltorena', 'Super Cucas - Micheltorena')

@order.route('/super-cucas-micheltorena/payment')
def super_cucas_micheltorena_payment():
    return handle_order_payment_request(request, '/super-cucas-micheltorena')

# request = flask request obj, account_email = restaurant accoutn email, url of form: '/restaurant-name-location'
def handle_order_website_request(request, account_email, url, restaurant_display_name):
    restaurant_user = User.query.filter_by(email_address=account_email).first()
    current_time = datetime.datetime.now()
    if current_time > restaurant_user.next_closing_time:
        restaurant_user.currently_accepting_orders = False
        restaurant_user.next_closing_time = calculate_next_closing_time(restaurant_user.closing_times)
        db.session.commit()
    elif ((current_time - restaurant_user.most_recent_time_orders_queried).total_seconds() > env['accepting_orders_autoshutoff_threshold_in_seconds']):
        restaurant_user.currently_accepting_orders = False
        db.session.commit()

    currently_accepting_orders = restaurant_user.currently_accepting_orders and restaurant_user.active_subscription and restaurant_user.stripe_charges_enabled

    if request.method == 'GET':
        return render_template('online-ordering-menu.html', menu=restaurant_user.json_menu, accepting_orders=currently_accepting_orders, restaurant_display_name=restaurant_display_name)
    elif request.method == 'POST':
        if not currently_accepting_orders:
            return redirect(url)
        
        order = ConvertJsonToOrder(json.loads(request.form['order']), url[1:]).order() # order being placed
        menu = ConvertJsonToMenu(json.loads(restaurant_user.json_menu), url[1:]).menu() # restaurant's menu to check the order against for validity

        if not order.is_valid_order(menu):
            return jsonify({'error': {'message': "Order invalid"}}), 400

        # price in cents
        payment_intent = stripe.PaymentIntent.create(
            payment_method_types=['card'],
            amount=int(order.price()*100),
            currency='usd',
            application_fee_amount=0,
            stripe_account=order.connected_account().stripe_connected_account_id,
            description=order.description(),
        )

        db_order = OrderClass(payment_intent_id=payment_intent.id, json_order=request.form['order'], paid=False, order_url=url[1:])
        db_order.add_to_db()

        session['stripe_client_secret'] = payment_intent.client_secret
        session['payment_intent_id'] = payment_intent.id
        session['order_price'] = payment_intent.amount
        session['stripe_connected_account_id'] = payment_intent.stripe_account

        return redirect(url + '/payment')

def handle_order_payment_request(request, url):
    if session.get('stripe_client_secret') and session.get('payment_intent_id') and session.get('order_price') and session.get('stripe_connected_account_id'):

        # Don't allow loading of payments page if session's payment_intent_id has already been paid for
        payment_intent = stripe.PaymentIntent.retrieve(
            session.get('payment_intent_id'),
            stripe_account=session.get('stripe_connected_account_id'),
        )
        if payment_intent.status == "succeeded":
            return redirect(url)

        return render_template('order-payment.html', stripe_client_secret=session['stripe_client_secret'], stripe_payment_intent_id=session['payment_intent_id'], stripe_publishable_api_key=env['stripe_publishable_api_key'], price=session['order_price'], stripe_connected_account_id=session['stripe_connected_account_id'])
    else:
        return redirect(url)

# POST endpoint for receiving the customer's name and setting the timestamp for the order
@order.route('/order/update-order-details', methods=['POST'])
def update_order_details():
    customer_name = request.form['customer_name']
    customer_email = request.form['customer_email']
    payment_intent_id = request.form['payment_intent_id']
    connected_account = request.form['connected_account']

    # update payment intent to include an email for receipts
    stripe.PaymentIntent.modify(
        payment_intent_id,
        stripe_account=connected_account,
        receipt_email=customer_email,
    )

    order = Order.query.filter_by(payment_intent_id=payment_intent_id).first()
    order.customer_name = customer_name[:50]
    order.customer_email = customer_email[:100]
    order.datetime = datetime.datetime.utcnow()
    db.session.commit()

    restaurant_user = User.query.filter_by(order_url=order.order_url).first()
    current_time = datetime.datetime.now()
    if current_time > restaurant_user.next_closing_time:
        restaurant_user.currently_accepting_orders = False
        restaurant_user.next_closing_time = calculate_next_closing_time(restaurant_user.closing_times)
        db.session.commit()
    elif ((current_time - restaurant_user.most_recent_time_orders_queried).total_seconds() > env['accepting_orders_autoshutoff_threshold_in_seconds']):
        restaurant_user.currently_accepting_orders = False
        db.session.commit()

    if restaurant_user.currently_accepting_orders and restaurant_user.active_subscription and restaurant_user.stripe_charges_enabled:
        return 'accepting orders'
    else:
        return 'not accepting orders'
