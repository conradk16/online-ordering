from flask import Blueprint, request, jsonify, session
import json
import stripe
from webapp.models.db_models import User, Order
from webapp import db, env
import json

webhook = Blueprint('webhook', __name__)

# POST endpoint for receiving Account webhooks from Stripe
@webhook.route('/webhook-account', methods=['POST'])
def webhook_account_received():
    webhook_secret = env['stripe_webhook_account_signing_secret']
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
        paid_for_hardware, paid_for_website = False, False
        line_items = stripe.checkout.Session.list_line_items(data_object.id, limit=2).data
        for line_item in line_items:
            if line_item.price.id == env['stripe_hardware_product_price_id']:
                paid_for_hardware = True
            if line_item.price.id == env['stripe_website_setup_product_price_id']:
                paid_for_website = True

        client_reference_id = data_object.client_reference_id
        stripe_customer_id = data_object.customer
        user = User.query.filter_by(email_address=client_reference_id).first()
        user.paid_for_hardware = paid_for_hardware
        user.paid_for_website = paid_for_website
        if data_object.shipping:
            user.shipping_address = json.dumps(data_object.shipping)
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
        # The payment failed or the customer does not have a valid payment method. The subscription becomes past_due.
        # Do nothing. Stripe will email them and prompt them to update their payment method.
        # If all retries fail, Stripe will cancel the subscription and trigger customer.subscription.deleted
        pass
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
    webhook_secret = env['stripe_webhook_connect_signing_secret']
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

    livemode = event['livemode']
    print(livemode)
    
    if event_type == 'account.updated':
        account_id = data_object.id
        user = User.query.filter_by(stripe_connected_account_id=account_id).first()
        user.stripe_connected_account_details_submitted = data_object.details_submitted
        user.stripe_charges_enabled = data_object.charges_enabled
        db.session.commit()
    elif event_type == "payment_intent.succeeded":
        payment_intent = data_object
        order = Order.query.filter_by(payment_intent_id=payment_intent.id).first()
        order.paid = True
        db.session.commit() 
    else:
      print('Unhandled event type {}'.format(event_type))

    return jsonify({'status': 'success'})


