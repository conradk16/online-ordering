from flask import Blueprint, request, jsonify
import json
import stripe

webhook = Blueprint('webhook', __name__)

# POST endpoint for receiving webhooks from Stripe
@webhook.route('/webhook', methods=['POST'])
def webhook_received():
    webhook_secret = whsec_nl7SSthz8v6VTonmCFHvB4sfZEtm5SPF
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
        print(data)
        # Payment is successful and the subscription is created.
        # You should provision the subscription and save the customer ID to your database.
    elif event_type == 'invoice.paid':
        print(data)
        # Continue to provision the subscription as payments continue to be made.
        # Store the status in your database and check when a user accesses your service.
        # This approach helps you avoid hitting rate limits.
    elif event_type == 'invoice.payment_failed':
        print(data)
        # The payment failed or the customer does not have a valid payment method.
        # The subscription becomes past_due. Notify your customer (email them) and send them to the
        # customer portal to update their payment information.
    else:
      print('Unhandled event type {}'.format(event_type))

    return jsonify({'status': 'success'})
