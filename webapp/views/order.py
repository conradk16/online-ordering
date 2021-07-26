from flask import Blueprint, render_template, request, jsonify, session, redirect, abort
from webapp.models.order import *
from webapp.models.db_models import User, Order
from webapp import db, env
from webapp.views.account import calculate_next_closing_time
import stripe
import json
import datetime
import re

order = Blueprint('order', __name__)

@order.route('/order/<order_url>', methods=['GET', 'POST'])
def route_handle_order_website_request(order_url):
    user = User.query.filter_by(order_url=order_url).first()
    if not user:
        abort(404)

    return handle_order_website_request(request, user)

@order.route('/payment/<order_url>')
def route_handle_order_payment_request(order_url):
    user = User.query.filter_by(order_url=order_url).first()
    if not user:
        abort(404)

    return handle_order_payment_request(request, user)

def handle_order_website_request(request, user):
    current_time = datetime.datetime.utcnow()
    if current_time > user.next_closing_time:
        user.currently_accepting_orders = False
        user.next_closing_time = calculate_next_closing_time(user.closing_times)
        db.session.commit()
    elif ((current_time - user.most_recent_time_orders_queried).total_seconds() > env['accepting_orders_autoshutoff_threshold_in_seconds']):
        user.currently_accepting_orders = False
        db.session.commit()

    currently_accepting_orders = user.currently_accepting_orders and user.active_subscription and user.stripe_charges_enabled

    if request.method == 'GET':
        return render_template('online-ordering-menu.html', menu=user.json_menu, accepting_orders=currently_accepting_orders, restaurant_display_name=user.restaurant_display_name)
    elif request.method == 'POST':
        if not currently_accepting_orders:
            return redirect('/order/' + user.order_url)
        
        order = ConvertJsonToOrder(json.loads(request.form['order']), user.order_url).order() # order being placed
        menu = ConvertJsonToMenu(json.loads(user.json_menu), user.order_url).menu() # restaurant's menu to check against for validity

        if not order.is_valid_order(menu):
            return jsonify({'error': {'message': "Order invalid"}}), 400

        # price in cents
        payment_intent = stripe.PaymentIntent.create(
            payment_method_types=['card'],
            amount=int(order.price()*100),
            currency='usd',
            application_fee_amount=0,
            stripe_account=user.stripe_connected_account_id,
            description=order.description(),
        )

        db_order = Order(payment_intent_id=payment_intent.id, json_order=request.form['order'], paid=False, order_url=user.order_url)
        db_order.add_to_db()

        session['stripe_client_secret'] = payment_intent.client_secret
        session['payment_intent_id'] = payment_intent.id
        session['order_price'] = payment_intent.amount
        session['stripe_connected_account_id'] = payment_intent.stripe_account

        return redirect('/payment/' + user.order_url)

def handle_order_payment_request(request, user):
    if session.get('stripe_client_secret') and session.get('payment_intent_id') and session.get('order_price') and session.get('stripe_connected_account_id'):

        # Don't allow loading of payments page if session's payment_intent_id has already been paid for
        payment_intent = stripe.PaymentIntent.retrieve(
            session.get('payment_intent_id'),
            stripe_account=session.get('stripe_connected_account_id'),
        )
        if payment_intent.status == "succeeded":
            return redirect('/order/' + user.order_url)

        return render_template('order-payment.html', stripe_client_secret=session['stripe_client_secret'], stripe_payment_intent_id=session['payment_intent_id'], stripe_publishable_api_key=env['stripe_publishable_api_key'], price=session['order_price'], stripe_connected_account_id=session['stripe_connected_account_id'])
    else:
        return redirect('/order/' + user.order_url)

# POST endpoint for receiving the customer's name and setting the timestamp for the order
@order.route('/update-order-details', methods=['POST'])
def update_order_details():
    customer_name = request.form['customer_name']
    customer_email = request.form['customer_email']
    payment_intent_id = request.form['payment_intent_id']
    connected_account = request.form['connected_account']

    if not True:
        return 'invalid email'

    try:
        # update payment intent to include an email for receipts
        stripe.PaymentIntent.modify(
            payment_intent_id,
            stripe_account=connected_account,
            receipt_email=customer_email,
        )
    except stripe.error.InvalidRequestError as e:
        if 'Invalid email address' in str(e):
            return 'invalid email'
        else:
            return 'failed to modify payment intent'
        

    order = Order.query.filter_by(payment_intent_id=payment_intent_id).first()
    order.customer_name = customer_name[:50]
    order.customer_email = customer_email[:100]
    order.datetime = datetime.datetime.utcnow()
    db.session.commit()

    restaurant_user = User.query.filter_by(order_url=order.order_url).first()
    current_time = datetime.datetime.utcnow()
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
