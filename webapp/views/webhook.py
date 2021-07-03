from flask import Blueprint, request, jsonify
import json
import stripe
from webapp.models.user import User
from webapp import db

import smtplib
from email.mime.text import MIMEText

webhook = Blueprint('webhook', __name__)

# POST endpoint for receiving webhooks from Stripe
@webhook.route('/webhook', methods=['POST'])
def webhook_received():
    webhook_secret = "whsec_aPIY1jxaG09Vy0UMfK0mVIDr5utNrUwU"
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
        client_reference_id = data_object.client_reference_id
        stripe_customer_id = data_object.customer
        user = User.query.filter_by(email_address=client_reference_id).first()
        user.stripe_customer_id = stripe_customer_id
        user.active_subscription = True
        db.session.commit()
    elif event_type == 'invoice.paid':
        stripe_customer_id = data_object.customer
        user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
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
        send_payment_failure_email(user.email_address)
    elif event_type == 'customer.subscription.deleted':
        # The customer cancelled the subscription and it has now ended
        stripe_customer_id = data_object.customer
        user = User.query.filter_by(stripe_customer_id=stripe_customer_id).first()
        user.active_subscription = False
        db.session.commit()
    else:
      print('Unhandled event type {}'.format(event_type))

    return jsonify({'status': 'success'})

def send_payment_failure_email(recipient_email_address):
    with open("../static/payment_failure_email_contents.txt", 'rb') as fp:
        # Create a text/plain message
        msg = MIMEText(fp.read())

    me = stefankuklinsky@gmail.com
    you = recipient_email_address
    
    msg['Subject'] = 'Payment Failure - M3 Orders'
    msg['From'] = me
    msg['To'] = you
    
    # Send the message via our own SMTP server, but don't include the envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()
