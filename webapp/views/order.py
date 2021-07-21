from flask import Blueprint, render_template, request, jsonify, session, redirect
from webapp.models.order import *
from webapp.models.db_models import User, Order
from webapp import db
import stripe
import json
import datetime
from webapp.views.account import calculate_next_closing_time

order = Blueprint('order', __name__)

menu_items, order_url = [], 'super-cucas-micheltorena'
menu_items.append(MenuItem("#1 Chorizo Burrito", "Mexican sausage, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#2 Protein Burrito", "Beef, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#3 Sausage Burrito", "Sausage scrambled eggs, cheese, and potatoes.", 10.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#4 Ham Burrito", "Ham, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#5 Veggie Burrito", "Grilled onions, bell peppers, zucchini, mushrooms, scrambled eggs, cheese, potatoes, and home style salsa.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#6 Carnitas Burrito", "Pork meat, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#7 Pastor Burrito", "Marinated pork meat, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#8 Eggs Burrito", "Scrambled eggs, cheese, and potatoes.", 7.99, [], [], "Breakfast"))
menu_items.append(MenuItem("#9 Ranchero Burrito", "Chorizo, bacon, scrambled eggs, cheese, potatoes, and ranchero salsa.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#10 Macho Burrito (Spicy)", "Marinated pork, jalapenos, scrambled eggs, cheese, potatoes, and macho salsa.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#11 Chicken Burrito", "Chicken, scrambled eggs, cheese, potatoes, and home style salsa.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#12 Energy Burrito", "Beef, veggies, scrambled eggs, cheese, potatoes, and home style salsa.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#13 Ham and Bacon Burrito", "Ham, bacon, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("#14 Breakfast Plate", "Choice of meat, eggs, cheese, rice, beans, and tortillas.", 7.99, [ChoiceSet("Meat", [Choice("Chicken", 1.00), Choice("Beef", 0), Choice("Pork", 0)]), ChoiceSet("Egg Style", [Choice("Scrambled", 0), Choice("Over Easy", 0), Choice("Over Medium", 0), Choice("Over Hard", 0), Choice("Sunny-Side Up", 0)])], [ChoiceSet("Goodies", [Choice("Brownies", 1.00), Choice("Sprinkles", 0)])], "Breakfast"))
menu_items.append(MenuItem("#15 Chile Relleno Burrito", "Pico de gallo, scrambled eggs, cheese, and potatoes.", 7.99, [],[], "Breakfast"))
menu_items.append(MenuItem("Shrimp Burrito", "Grilled vegetables, rice, beans, cheese, and pico de gallo.", 11.94, [],[], "Burritos"))
menu_items.append(MenuItem("Combo Burrito", "Cheese, sour cream, onion, and cilantro.", 10.99, [],[], "Burritos"))

super_cucas_menu = Menu(menu_items, order_url)


@order.route('/super-cucas-micheltorena', methods=['GET', 'POST'])
def super_cucas_micheltorena():

    restaurant_user = User.query.filter_by(order_url=super_cucas_menu.order_url).first()
    current_time = datetime.datetime.now()
    if current_time > restaurant_user.next_closing_time:
        restaurant_user.currently_accepting_orders = False
        restaurant_user.next_closing_time = calculate_next_closing_time(restaurant_user.closing_times)
        db.session.commit()
    elif ((current_time - restaurant_user.most_recent_time_orders_queried).total_seconds() > 300):
        restaurant_user.currently_accepting_orders = False
        db.session.commit()

    currently_accepting_orders = restaurant_user.currently_accepting_orders and restaurant_user.active_subscription
    
    if request.method == 'GET':
        return render_template('super-cucas-micheltorena.html', menu=json.dumps(super_cucas_menu, default=lambda x:x.__dict__), accepting_orders=currently_accepting_orders)
    elif request.method == 'POST':

        if not currently_accepting_orders:
            return redirect('/super-cucas-micheltorena')
        
        order = ConvertJsonToOrder(json.loads(request.form['order']), super_cucas_menu.order_url).order()

        if not order.is_valid_order(super_cucas_menu):
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

        db_order = Order(payment_intent_id=payment_intent.id, json_order=request.form['order'], paid=False, order_url=super_cucas_menu.order_url)
        db_order.add_to_db()

        session['stripe_client_secret'] = payment_intent.client_secret
        session['payment_intent_id'] = payment_intent.id
        session['order_price'] = payment_intent.amount
        session['stripe_connected_account_id'] = payment_intent.stripe_account

        return redirect('/super-cucas-micheltorena/payment')

@order.route('/super-cucas-micheltorena/payment')
def super_cucas_micheltorena_payment():

    if session.get('stripe_client_secret') and session.get('payment_intent_id') and session.get('order_price') and session.get('stripe_connected_account_id'):

        # Don't allow loading of payments page if session's payment_intent_id has already been paid for
        payment_intent = stripe.PaymentIntent.retrieve(
            session.get('payment_intent_id'),
            stripe_account=session.get('stripe_connected_account_id'),
        )
        if payment_intent.status == "succeeded":
            return redirect('/super-cucas-micheltorena')

        return render_template('order-payment.html', stripe_client_secret=session['stripe_client_secret'], stripe_payment_intent_id=session['payment_intent_id'], price=session['order_price'], stripe_connected_account_id=session['stripe_connected_account_id'])
    else:
        return redirect('/super-cucas-micheltorena')

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
    elif ((current_time - restaurant_user.most_recent_time_orders_queried).total_seconds() > 300):
        restaurant_user.currently_accepting_orders = False
        db.session.commit()

    if restaurant_user.currently_accepting_orders and restaurant_user.active_subscription:
        return 'accepting orders'
    else:
        return 'not accepting orders'
