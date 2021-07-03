from flask import Flask, render_template, redirect, session, request, jsonify
import stripe
import json

application = Flask(__name__)

stripe.api_key = 'sk_test_51J8elwLGQW192ovfZdXa5R8KnXuzvceiy9kCV7wojYHBG3L4Y0H0W4MjpXFTgZhUEw9Qzn1naBr5mR2MXUCnczOo00nsenWbzL'

# homepage
@application.route('/')
def company_homepage():
    return render_template('company-homepage.html')

# POST endpoint for businesses to pay us - requires an HTML form and redirects them to Stripe's checkout URL
@application.route('/create-checkout-session', methods=['POST'])
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

# webhook that receives Stripe notifications (eg that a business has successfully paid for the subscription)
@application.route('/webhook', methods=['POST'])
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


# login page
@application.route('/login')
def login_page():
    if session.get('logged_in'):
        return redirect(url_for('account_homepage', username=session.get('username')))
    else:
        return render_template('login-page.html')

# account page
@application.route('/account/<username>')
def account_homepage(username):
    return render_template('account-homepage.html')

# GET endpoint for business onboarding - redirects to Stripe link where businesses can onboard with Stripe
@application.route('/stripe/connect-with-stripe')
def connect_with_stripe():

    # create account
    account = stripe.Account.create(
        type='standard',
    )

    # create account link (a Stripe URL) where the user can onboard with Stripe
    account_link_object = stripe.AccountLink.create(
        account=account.id,
        refresh_url='https://m3orders.com',
        return_url='https://m3orders.com',
        type='account_onboarding',
    )

    return redirect(account_link_object.url)

# manually created online-ordering website for a specific business, should be created after the business onboards.
# check the business's payment status and if past due by x days, don't render_template their website
@application.route('/super-cucas-micheltorena')
def super_cucas_micheltorena():
    return render_template('super-cucas-micheltorena.html')


if __name__ == "__main__":
    application.debug = True
    application.run()
