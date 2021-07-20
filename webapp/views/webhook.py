from flask import Blueprint, request, jsonify, session
import json
import stripe
from webapp.models.db_models import User, Order
from webapp import db

webhook = Blueprint('webhook', __name__)

# POST endpoint for receiving Account webhooks from Stripe
@webhook.route('/webhook-account', methods=['POST'])
def webhook_account_received():
    #webhook_secret = "whsec_aPIY1jxaG09Vy0UMfK0mVIDr5utNrUwU" # TEST INTEGRATION WEBHOOK
    webhook_secret = "whsec_XDeJeqt7NpBy9HfWB5qmd4iO9dCrtmap" # TEST localhost webhook
    request_data = json.loads(request.data)

    signature = request.headers.get('stripe-signature')
    try:
        event = stripe.Webhook.construct_event(
            payload=request.data, sig_header=signature, secret=webhook_secret)
        data = event['data']
    except Exception as e:
        return e

    event_type = event['type']
    data_object = data['object']
    
    if event_type == 'checkout.session.completed':
        # Payment is successful and the subscription is created.

        # Check if paid for hardware
        paid_for_hardware = False
        line_items = stripe.checkout.Session.list_line_items(data_object.id, limit=2).data
        for line_item in line_items:
            if line_item.price.id == "price_1JFMNILGQW192ovflSPEK3sp":
                paid_for_hardware = True

        client_reference_id = data_object.client_reference_id
        stripe_customer_id = data_object.customer
        user = User.query.filter_by(email_address=client_reference_id).first()
        user.paid_for_hardware = paid_for_hardware
        user.stripe_customer_id = stripe_customer_id
        user.active_subscription = True
        db.session.commit()
    elif event_type == 'invoice.paid':
        stripe_customer_id = data_object.customer
        user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()

        # If invoice.paid webhook sent right when checkout.session.completed, user might not have stripe_customer_id assigned to them yet
        if user:
            user.active_subscription = True
            db.session.commit()
    elif event_type == 'invoice.payment_failed':
        # The payment failed or the customer does not have a valid payment method.
        # The subscription becomes past_due. Notify your customer (email them) and send them to the
        # customer portal to update their payment information.
        stripe_customer_id = data_object.customer
        user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
        user.active_subscription = False
        db.session.commit()
    elif event_type == 'customer.subscription.deleted':
        # The customer cancelled the subscription and it has now ended
        stripe_customer_id = data_object.customer
        user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
        user.active_subscription = False
        db.session.commit()
    else:
      print('Unhandled event type {}'.format(event_type))

    return jsonify({'status': 'success'})

# POST endpoint for receiving Connect webhooks from Stripe
@webhook.route('/webhook-connect', methods=['POST'])
def webhook_connect_received():
    #webhook_secret = "whsec_ou3eKzCLgsvLSM8CuYgirpXhatVsArlE" # TEST INTEGRATION WEBHOOK
    webhook_secret = "whsec_eKndjsZQ3ShaeMdqo5wp13gziZLI7as5" # TEST localhost webhook
    request_data = json.loads(request.data)

    signature = request.headers.get('stripe-signature')
    try:
        event = stripe.Webhook.construct_event(
            payload=request.data, sig_header=signature, secret=webhook_secret)
        data = event['data']
    except Exception as e:
        return e

    event_type = event['type']
    data_object = data['object']
    
    if event_type == 'account.updated':
        account_id = data_object.id
        user = User.query.filter_by(stripe_connected_account_id=account_id).first()
        user.stripe_connected_account_details_submitted = data_object.details_submitted
        db.session.commit()
    elif event_type == "payment_intent.succeeded":
        payment_intent = data_object
        order = Order.query.filter_by(payment_intent_id=payment_intent.id).first()
        order.paid = True
        db.session.commit() 
    else:
      print('Unhandled event type {}'.format(event_type))

    return jsonify({'status': 'success'})


