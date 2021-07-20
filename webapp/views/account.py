from flask import Blueprint, render_template, redirect, abort, send_file, request, jsonify
from flask_mail import Message
import stripe
from webapp import db, mail
from webapp.models.db_models import User, Order
from flask_login import login_user, logout_user, current_user
import json
import datetime, pytz

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

@account.route('/account/setup')
def signup_test():
    return render_template('signup-enter-account-details.html')

@account.route('/account/setup-hours')
def hours_temp():
    return render_template('signup-setup-hours.html')


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

        for order in Order.query.filter_by(order_url=current_user.order_url, paid=True, marked_as_complete_by_restaurant=False, refunded=False).order_by(Order.datetime.desc()):
            d = {}
            d['json_order'] = order.json_order
            d['refunded_status'] = order.refunded
            d['marked_as_complete_by_restaurant'] = order.marked_as_complete_by_restaurant
            d['datetime'] = order.datetime
            d['payment_intent_id'] = order.payment_intent_id
            d['customer_name'] = order.customer_name.split()[0][:20] # just get first name, take 20 characters max
            pending_orders.append(d)

        if len(pending_orders) == 0:
            pending_orders = "No orders"

        archived_orders = []

        for order in Order.query.filter_by(order_url=current_user.order_url, paid=True).filter((Order.marked_as_complete_by_restaurant == True) | (Order.refunded == True)).order_by(Order.datetime.asc()):
            d = {}
            d['json_order'] = order.json_order
            d['refunded_status'] = order.refunded
            d['marked_as_complete_by_restaurant'] = order.marked_as_complete_by_restaurant
            d['datetime'] = order.datetime
            d['payment_intent_id'] = order.payment_intent_id
            d['customer_name'] = order.customer_name.split()[0][:20]
            archived_orders.append(d)

        if len(archived_orders) == 0:
            archived_orders = "No orders"


        currently_accepting_orders = "true" if current_user.currently_accepting_orders else "false"
        return render_template('view-orders.html', pending_orders=pending_orders, archived_orders=archived_orders, currently_accepting_orders=currently_accepting_orders)
    else:
        return redirect('/login')

# POST endpoint for getting an updated order list without refreshing the page
@account.route('/account/get-updated-orders', methods=['POST'])
def get_updated_orders():
    if current_user.is_authenticated:
        pending_orders = []

        for order in Order.query.filter_by(order_url=current_user.order_url, paid=True, marked_as_complete_by_restaurant=False, refunded=False).order_by(Order.datetime.desc()):
            d = {}
            d['json_order'] = order.json_order
            d['refunded_status'] = order.refunded
            d['marked_as_complete_by_restaurant'] = order.marked_as_complete_by_restaurant
            d['datetime'] = order.datetime
            d['payment_intent_id'] = order.payment_intent_id
            d['customer_name'] = order.customer_name.split()[0][:20]
            pending_orders.append(d)

        if len(pending_orders) == 0:
            pending_orders = "No orders"

        archived_orders = []

        for order in Order.query.filter_by(order_url=current_user.order_url, paid=True).filter((Order.marked_as_complete_by_restaurant == True) | (Order.refunded == True)).order_by(Order.datetime.asc()):
            d = {}
            d['json_order'] = order.json_order
            d['refunded_status'] = order.refunded
            d['marked_as_complete_by_restaurant'] = order.marked_as_complete_by_restaurant
            d['datetime'] = order.datetime
            d['payment_intent_id'] = order.payment_intent_id
            d['customer_name'] = order.customer_name.split()[0][:20]
            archived_orders.append(d)

        if len(archived_orders) == 0:
            archived_orders = "No orders"

        currently_accepting_orders = "true" if current_user.currently_accepting_orders else "false"

        return jsonify([pending_orders, archived_orders, currently_accepting_orders])
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
        order = Order.query.filter_by(payment_intent_id=request.form['payment_intent_id']).first()
        if request.form['order_completed_status'] == 'true':
            order.marked_as_complete_by_restaurant = True
        else:
            order.marked_as_complete_by_restaurant = False
        db.session.commit()
        return "success"
    else:
        return redirect('/login')

# POST endpoint for refunding orders
@account.route('/account/refund-order', methods=['POST'])
def refund_order():
    if current_user.is_authenticated:
        payment_intent_id = request.form['payment_intent_id']
        rejection_description = request.form['reject_order_description']

        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            stripe_account=current_user.stripe_connected_account_id,
        )

        order = Order.query.filter_by(payment_intent_id=payment_intent_id).first()
        order.refunded = True
        db.session.commit()

        send_order_refunded_email(order.customer_email, rejection_description)

        return "success"
    else:
        return "failure"

def calculate_next_closing_time(closing_times):
    current_time = datetime.datetime.now()

    next_closing_times = []

    # ['US/Alaska', 'US/Aleutian', 'US/Arizona', 'US/Central', 'US/East-Indiana', 'US/Eastern', 'US/Hawaii', 'US/Indiana-Starke', 'US/Michigan', 'US/Mountain', 'US/Pacific', 'US/Samoa']
    # closing_time is a dict: {"day": 0-6, "hour": 0-60, "minute": 0-60, "timezone": "US/Alaska"}
    for closing_time in closing_times:
        current_time_in_new_tz = current_time.astimezone(pytz.timezone(closing_time['timezone']))
        next_closing_time = current_time_in_new_tz

        while next_closing_time.weekday() != closing_time['day']:
            next_closing_time += datetime.timedelate(1)
        while next_closing_time.hour != closing_time['hour']:
            next_closing_time += datetime.timedelta(hours=1)
        while next_closing_time.minute != closing_time['minute']:
            next_closing_time += datetime.timedelta(minutes=1)

        next_closing_times.append(next_closing_time)

    return min(next_closing_times)
        
def calculate_next_time

def convertTimeToSpecificTimezone(time, timezone):
    return timezone.localize(datetime.combine(datetime.today(), t)).timetz()

def send_order_refunded_email(customer_email, rejection_description):

    msg = Message(subject='Order Could Not be Fulfilled', sender="no-reply@m3orders.com", recipients=[customer_email])
    msg.html = render_template('order-rejected-email.html', rejection_description=rejection_description)
    mail.send(msg)

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
