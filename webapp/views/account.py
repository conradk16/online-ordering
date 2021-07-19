from flask import Blueprint, render_template, redirect, abort, send_file, request, jsonify
import stripe
from webapp import db
from webapp.models.db_models import User, Order
from flask_login import login_user, logout_user, current_user
import json

account = Blueprint('account', __name__)

# account homepage
@account.route('/account/')
def account_homepage():
    if current_user.is_authenticated:
        if current_user.email_address == "kuklinskywork@gmail.com":
            return get_admin_page()
        elif current_user.stripe_customer_id:
            return render_template('account.html', connected_with_stripe=current_user.stripe_connected_account_details_submitted)
        else:
            return redirect('/signup/select-plan')
    else:
        return redirect('/login')


# GET endpoint for Connect With Stripe button, redirects to Stripe onboarding link
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

# GET endpoint for viewing orders
@account.route('/account/orders')
def view_orders():
    if current_user.is_authenticated:
        pending_orders = []

        for order in Order.query.filter_by(order_url=current_user.order_url, paid=True, marked_as_complete_by_restaurant=False):
            d = {}
            d['json_order'] = order.json_order
            d['rejected_status'] = order.rejected_by_restaurant
            d['marked_as_complete_by_restaurant'] = order.marked_as_complete_by_restaurant
            d['datetime'] = order.datetime
            d['client_secret'] = order.client_secret
            d['customer_name'] = order.customer_name.split()[0]
            pending_orders.append(d)
        
        if len(pending_orders) == 0:
            pending_orders = "No orders"

        archived_orders = []

        for order in Order.query.filter_by(order_url=current_user.order_url, paid=True, marked_as_complete_by_restaurant=True):
            d = {}
            d['json_order'] = order.json_order
            d['rejected_status'] = order.rejected_by_restaurant
            d['marked_as_complete_by_restaurant'] = order.marked_as_complete_by_restaurant
            d['datetime'] = order.datetime
            d['client_secret'] = order.client_secret
            d['customer_name'] = order.customer_name.split()[0]
            archived_orders.append(d)
        
        if len(archived_orders) == 0:
            archived_orders = "No orders"


        currently_accepting_orders = "true" if current_user.currently_accepting_orders else "false"
        return render_template('view-orders.html', pending_orders=pending_orders, archived_orders=archived_orders, currently_accepting_orders=currently_accepting_orders)
    else:
        return redirect('/login')

# POST endpoint for toggling currently_accepting_orders
@account.route('/account/update-accepting-orders-status', methods=['POST'])
def update_accepting_orders_status():
    if current_user.is_authenticated:
        if request.form['currently_accepting_orders'] == 'true':
            current_user.currently_accepting_orders = True
            db.session.commit()
            return "accepting orders"
        else:
            current_user.currently_accepting_orders = False
            db.session.commit()
            return "not accepting orders"
    else:
        return redirect('/login')

# POST endpoint for updating order completed status
@account.route('/account/update-order-marked-as-complete-status', methods=['POST'])
def update_order_marked_as_complete_status():
    if current_user.is_authenticated:
        order = Order.query.filter_by(client_secret=request.form['client_secret']).first()
        if request.form['order_completed_status'] == 'true':
            order.marked_as_complete_by_restaurant = True
        else:
            order.marked_as_complete_by_restaurant = False
        db.session.commit()
        return "success"
    else:
        return redirect('/login')

# POST endpoint for getting an updated order list without refreshing the page
@account.route('/account/get-updated-orders', methods=['POST'])
def get_updated_orders():
    if current_user.is_authenticated:
        pending_orders = []

        for order in Order.query.filter_by(order_url=current_user.order_url, paid=True, marked_as_complete_by_restaurant=False):
            d = {}
            d['json_order'] = order.json_order
            d['rejected_status'] = order.rejected_by_restaurant
            d['marked_as_complete_by_restaurant'] = order.marked_as_complete_by_restaurant
            d['datetime'] = order.datetime
            d['client_secret'] = order.client_secret
            d['customer_name'] = order.customer_name.split()[0]
            pending_orders.append(d)
        
        if len(pending_orders) == 0:
            pending_orders = "No orders"

        archived_orders = []

        for order in Order.query.filter_by(order_url=current_user.order_url, paid=True, marked_as_complete_by_restaurant=True):
            d = {}
            d['json_order'] = order.json_order
            d['rejected_status'] = order.rejected_by_restaurant
            d['marked_as_complete_by_restaurant'] = order.marked_as_complete_by_restaurant
            d['datetime'] = order.datetime
            d['client_secret'] = order.client_secret
            d['customer_name'] = order.customer_name.split()[0] # just get first name
            archived_orders.append(d)
        
        if len(archived_orders) == 0:
            archived_orders = "No orders"

        return jsonify([pending_orders, archived_orders])
    else:
        return redirect('/login')

def get_admin_page():
    users_without_websites = User.query.filter_by(order_url=None, stripe_connected_account_details_submitted=True)
    account_emails_without_websites = [user_without_website.email_address for user_without_website in users_without_websites]
    return render_template('admin.html', account_emails_without_websites=account_emails_without_websites)

@account.route('/account/admin-download-database')
def admin_download_database():
    if current_user.is_authenticated and current_user.email_address == "kuklinskywork@gmail.com":
        return send_file("database.db", as_attachment=True)
    else:
        abort(404)

@account.route('/account/admin-assign-url-to-account', methods=['POST'])
def admin_assign_url_to_account():
    if current_user.is_authenticated and current_user.email_address == "kuklinskywork@gmail.com":
        account_email = request.form['email_address']
        account_url = request.form['url']
        user = User.query.filter_by(email_address=account_email).first()
        user.order_url = account_url
        db.session.commit()
    return redirect('/account')
