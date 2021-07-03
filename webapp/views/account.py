from flask import Blueprint, render_template, redirect
import stripe

account = Blueprint('account', __name__)

# account page
@account.route('/account/')
def account_homepage():
    return render_template('account-homepage.html')


# POST endpoint for Connect With Stripe button, redirects to Stripe onboarding link
@account.route('/account/connect-with-stripe', methods=['POST'])
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

