from flask import Blueprint, render_template, redirect
import stripe

account = Blueprint('account', __name__)

# account homepage
@account.route('/account/')
def account_homepage():
    return render_template('account-homepage.html')


# POST endpoint for Connect With Stripe button, redirects to Stripe onboarding link
@account.route('/account/connect-with-stripe')
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

# POST endpoint for customers to manage their billing
@account.route('/account/manage-billing', methods=['POST'])
def manage_billing():
    return_url = "https://m3orders.com/account"
    
    session = stripe.billing_portal.Session.create(
        customer='{{CUSTOMER_ID}}',
        return_url=return_url)
    
    return redirect(session.url)
