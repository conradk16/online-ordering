from flask import Blueprint, render_template, request, jsonify, session, redirect
from webapp.models.order import MenuItem, OrderItem, ChoiceSet, Choice
from webapp.models.user import User
from webapp import db
import stripe
import json

order = Blueprint('order', __name__)

super_cucas_menu = []
super_cucas_menu.append(MenuItem("#1 Chorizo Burrito", "Mexican sausage, scrambled eggs, cheese, and potatoes.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#2 Protein Burrito", "Beef, scrambled eggs, cheese, and potatoes.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#3 Sausage Burrito", "Sausage scrambled eggs, cheese, and potatoes.", 10.99, [],[]))
super_cucas_menu.append(MenuItem("#4 Ham Burrito", "Ham, scrambled eggs, cheese, and potatoes.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#5 Veggie Burrito", "Grilled onions, bell peppers, zucchini, mushrooms, scrambled eggs, cheese, potatoes, and home style salsa.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#6 Carnitas Burrito", "Pork meat, scrambled eggs, cheese, and potatoes.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#7 Pastor Burrito", "Marinated pork meat, scrambled eggs, cheese, and potatoes.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#8 Eggs Burrito", "Scrambled eggs, cheese, and potatoes.", 7.99, [], []))
super_cucas_menu.append(MenuItem("#9 Ranchero Burrito", "Chorizo, bacon, scrambled eggs, cheese, potatoes, and ranchero salsa.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#10 Macho Burrito (Spicy)", "Marinated pork, jalapenos, scrambled eggs, cheese, potatoes, and macho salsa.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#11 Chicken Burrito", "Chicken, scrambled eggs, cheese, potatoes, and home style salsa.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#12 Energy Burrito", "Beef, veggies, scrambled eggs, cheese, potatoes, and home style salsa.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#13 Ham and Bacon Burrito", "Ham, bacon, scrambled eggs, cheese, and potatoes.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("#14 Breakfast Plate", "Choice of meat, eggs, cheese, rice, beans, and tortillas.", 7.99, [ChoiceSet("Meat", [Choice("Chicken", 1.00), Choice("Beef", 0), Choice("Pork", 0)]), ChoiceSet("Egg Style", [Choice("Scrambled", 0), Choice("Over Easy", 0), Choice("Over Medium", 0), Choice("Over Hard", 0), Choice("Sunny-Side Up", 0)])], [ChoiceSet("Goodies", [Choice("Brownies", 1.00), Choice("Sprinkles", 0)])]))
super_cucas_menu.append(MenuItem("#15 Chile Relleno Burrito", "Pico de gallo, scrambled eggs, cheese, and potatoes.", 7.99, [],[]))
super_cucas_menu.append(MenuItem("Shrimp Burrito", "Grilled vegetables, rice, beans, cheese, and pico de gallo.", 11.94, [],[]))
super_cucas_menu.append(MenuItem("Combo Burrito", "Cheese, sour cream, onion, and cilantro.", 10.99, [],[]))


@order.route('/super-cucas-micheltorena', methods=['GET', 'POST'])
def super_cucas_micheltorena():
    if request.method == 'GET':
        return render_template('super-cucas-micheltorena.html')
    elif request.method == 'POST':
        json_order_items = request.json['cart_items']
        order_items = []
        for json_order_item in json_order_items:
            order_items.append(json_order_item_to_class(json_order_item))
    
        if not is_valid_order(order_items):
            print("Order invalid")
            return jsonify({'error': {'message': "Order invalid"}}), 400

        order_price = sum([order_item.price() for order_item in order_items])

        connected_stripe_account_id = User.query.filter_by(order_url="super-cucas-micheltorena").first().stripe_connected_account_id

        payment_intent = stripe.PaymentIntent.create(
            payment_method_types=['card'],
            amount=order_price,
            currency='usd',
            application_fee_amount=0,
            stripe_account=connected_stripe_account_id,
        )

        session['stripe_client_secret'] = payment_intent.client_secret

        return redirect('/super-cucas-micheltorena/payment')


@order.route('/super-cucas-micheltorena/payment', methods=['GET', 'POST'])
def super_cucas_micheltorena_payment():

    if request.method == 'GET':
        return render_template('super-cucas-micheltorena-payment', stripe_client_secret=session['stripe_client_secret'])


def json_order_item_to_class(json_order_item):
    menu_item = json_menu_item_to_class(json_order_item['item'])
    required_selections = []
    for json_required_selection in json_order_item['required_selections']:
        required_selections.append(Choice(json_required_selection['name'], json_required_selection['price']))
    optional_selections = []
    for json_optional_selection in json_order_item['optional_selections']:
        optional_selections.append(Choice(json_optional_selection['name'], json_optional_selection['price']))
    return OrderItem(menu_item, required_selections, optional_selections, json_order_item['quantity'], json_order_item['special_instructions'])


def json_menu_item_to_class(json_menu_item):
    required_choice_sets = []
    for json_required_choice_set in json_menu_item['required_choice_sets']:
        required_choice_sets.append(json_choice_set_to_class(json_required_choice_set))
    optional_choice_sets = []
    for json_optional_choice_set in json_menu_item['optional_choice_sets']:
        optional_choice_sets.append(json_choice_set_to_class(json_optional_choice_set))
    return MenuItem(json_menu_item['item_name'], json_menu_item['item_description'], json_menu_item['price'], required_choice_sets, optional_choice_sets)


def json_choice_set_to_class(json_choice_set):
    choices = []
    for json_choice in json_choice_set['choices']:
        choices.append(Choice(json_choice['name'], json_choice['price']))
    return ChoiceSet(json_choice_set['title'], choices)

def is_valid_order(order_items):
    for order_item in order_items:

        # menu item must be part of the menu
        if order_item.menu_item not in super_cucas_menu:
            return False

        # all required selections must be unique
        if not (len(order_item.required_selections) == len(set(order_item.required_selections))):
            return False

        # all optional selections must be unique
        if not (len(order_item.optional_selections) == len(set(order_item.optional_selections))):
            return False

        # all required selections must be an option given by the menu
        for required_selection in order_item.required_selections:
            if not any([required_selection in choice_set.choices for choice_set in order_item.menu_item.required_choice_sets]):
                return False

        # all optional selections must be an option given by the menu
        for optional_selection in order_item.optional_selections:
            if not any([optional_selection in choice_set.choices for choice_set in order_item.menu_item.optional_choice_sets]):
                return False

    return True

