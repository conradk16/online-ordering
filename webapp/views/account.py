from flask import Blueprint, render_template, redirect
import stripe
from webapp import db
from webapp.models.user import User
from flask_login import login_user, logout_user, current_user 

account = Blueprint('account', __name__)

# account homepage
@account.route('/account/')
def account_homepage():
    if current_user.is_authenticated:
        return render_template('account-homepage.html', connected_with_stripe=current_user.stripe_connected_account_details_submitted)
    else:
        return redirect('/login')


# POST endpoint for Connect With Stripe button, redirects to Stripe onboarding link
@account.route('/account/connect-with-stripe')
def connect_with_stripe():

    if current_user.is_authenticated:
        # Use existing connected account if they have one, otherwise create account and store account.id in the Users table
        account_id = current_user.stripe_connected_account_id
        if not account_id:
            account = stripe.Account.create(
                type='standard',
            )
            account_id = account.id
            current_user.stripe_connected_account_id = account_id
            db.session.commit()

        # create account link (a Stripe URL) where the user can onboard with Stripe
        account_link_object = stripe.AccountLink.create(
            account=account_id,
            refresh_url='https://m3orders.com/account',
            return_url='https://m3orders.com/account',
            type='account_onboarding',
        )

        return redirect(account_link_object.url)
    else:
        return redirect('/login')

# POST endpoint for customers to manage their billing
@account.route('/account/manage-billing', methods=['POST'])
def manage_billing():
    session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url="https://m3orders.com/account")
    
    return redirect(session.url)
