from flask import Blueprint, render_template, redirect, abort, send_file, request, jsonify
from flask_mail import Message
import stripe
from webapp import db, mail, env
from webapp.models.db_models import User, Order
from flask_login import login_user, logout_user, current_user
import json
import datetime, pytz
import io

account = Blueprint('account', __name__)

# account homepage
@account.route('/account/')
def account_homepage():
    if not current_user.is_authenticated:
        return redirect('/login')
    elif current_user.email_address == env['admin_username']:
        return get_admin_page()
    elif not current_user.stripe_customer_id:
        return redirect('/signup/select-website')
    elif not current_user.account_details:
        return redirect('/account/setup-account-details')
    elif not current_user.menu_notes:
        return redirect('/account/setup-menu-notes')
    elif not current_user.closing_times:
        return redirect('/account/setup-closing-times')
    elif not current_user.stripe_connected_account_details_submitted:
        return redirect('/account/setup-stripe')
    else:
        return render_template('account.html', order_url=current_user.order_url, active_subscription=current_user.active_subscription, paid_for_website=current_user.paid_for_website, website_url=current_user.website_url)

@account.route('/account/setup-account-details', methods=['GET', 'POST'])
def enter_account_details():
    if not current_user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        if not current_user.stripe_customer_id:
            return redirect('/signup/select-plan')

        return render_template('setup-account-details.html')
    elif request.method == 'POST':
        if not  is_valid_setup_account_details_post_request(request):
            return redirect('/account')
        
        account_details = {}
        account_details['name'] = request.form['name']
        account_details['email'] = request.form['email']
        account_details['phone'] = request.form['phone']
        account_details['restaurant_name'] = request.form['restaurant_name']
        account_details['restaurant_address'] = request.form['restaurant_address']
        account_details['menu_url'] = request.form['menu_url'] if ('menu_url' in request.form) else ''

        current_user.account_details = json.dumps(account_details)

        if 'menu_file' in request.files:
            current_user.menu_file = request.files['menu_file'].read()
            current_user.menu_file_filename = request.files['menu_file'].filename

        db.session.commit()

        return redirect('/account/setup-menu-notes')


@account.route('/account/setup-menu-notes', methods=['GET', 'POST'])
def setup_menu_notes():
    if not current_user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        if not current_user.stripe_customer_id:
            return redirect('/signup/select-plan')
        elif not current_user.account_details:
            return redirect('/account/setup-account-details')
        else:
            return render_template('setup-menu-notes.html')
    elif request.method == 'POST':
        if not is_valid_menu_notes_post_request(request):
            return redirect('/account')
        
        if len(request.form['menu_notes']) == 0:
            current_user.menu_notes = 'No menu notes'
        else:
            current_user.menu_notes = request.form['menu_notes']
        db.session.commit()
        return redirect('/account/setup-closing-times')


@account.route('/account/setup-closing-times', methods=['GET', 'POST'])
def setup_closing_hours():
    if not current_user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        if not current_user.stripe_customer_id:
            return redirect('/signup/select-plan')
        elif not current_user.account_details:
            return redirect('/account/setup-account-details')
        elif not current_user.menu_notes:
            return redirect('/account/setup-menu-notes')
        else:
            return render_template('setup-closing-hours.html')
    elif request.method == 'POST':
        if not is_valid_closing_times_post_request(request):
            return redirect('/account')
        
        current_user.closing_times = request.form['closing_times']
        current_user.next_closing_time = calculate_next_closing_time(request.form['closing_times'])
        db.session.commit()
        
        return redirect('/account/setup-stripe')

@account.route('/account/setup-stripe', methods=['GET', 'POST'])
def setup_stripe():
    if not current_user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        if not current_user.stripe_customer_id:
            return redirect('/signup/select-plan')
        elif not current_user.account_details:
            return redirect('/account/setup-account-details')
        elif not current_user.menu_notes:
            return redirect('/account/setup-menu-notes')
        elif not current_user.closing_times:
            return redirect('/account/setup-closing-times')
        elif current_user.stripe_connected_account_details_submitted:
            return redirect('/account')
        else:
            return render_template('setup-stripe.html')
    elif request.method == 'POST':
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
            refresh_url=env['stripe_account_link_refresh_url'],
            return_url=env['stripe_account_link_return_url'],
            type='account_onboarding',
        )

        return redirect(account_link_object.url)

@account.route('/account/account-details', methods=['GET', 'POST'])
def edit_account_details():
    if not current_user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        if not current_user.stripe_connected_account_details_submitted:
            return redirect('/account/setup-stripe')
        return render_template('edit-account-details.html', account_details=current_user.account_details, order_url=current_user.order_url, active_subscription=current_user.active_subscription, menu_filename=current_user.menu_file_filename)
    elif request.method == 'POST':
        if not is_valid_edit_account_details_post_request(request):
            return redirect('/account/account-details')
        
        current_account_details = json.loads(current_user.account_details)

        current_account_details['name'] = request.form['name']
        current_account_details['email'] = request.form['email']
        current_account_details['phone'] = request.form['phone']
        current_account_details['menu_url'] = request.form['menu_url'] if ('menu_url' in request.form) else ''

        current_user.account_details = json.dumps(current_account_details)

        if 'menu_file' in request.files and request.files['menu_file'].filename:
            current_user.menu_file = request.files['menu_file'].read()
            current_user.menu_file_filename = request.files['menu_file'].filename

        db.session.commit()

        return redirect('/account')

@account.route('/account/closing-times', methods=['GET', 'POST'])
def edit_closing_times():
    if not current_user.is_authenticated:
        return redirect('/login')

    if request.method == 'GET':
        if not current_user.stripe_connected_account_details_submitted:
            return redirect('/account/setup-stripe')
        return render_template('edit-closing-hours.html', closing_times=current_user.closing_times, order_url=current_user.order_url, active_subscription=current_user.active_subscription)
    elif request.method == 'POST':
        if not is_valid_closing_times_post_request(request):
            return redirect('/account/closing-times')

        current_user.closing_times = request.form['closing_times']
        current_user.next_closing_time = calculate_next_closing_time(request.form['closing_times'])
        db.session.commit()
        
        return redirect('/account')


# GET endpoint that redirects customers to manage their billing
@account.route('/account/manage-subscription')
def manage_subcription():
    if not current_user.is_authenticated:
        return redirect('/login')
    if not current_user.stripe_customer_id:
        return redirect('/signup/select-plan')
    
    session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=env['stripe_billing_portal_return_url'])

    return redirect(session.url)

# GET endpoint for viewing orders
@account.route('/account/orders')
def view_orders():
    if current_user.is_authenticated:

        if not current_user.stripe_connected_account_details_submitted:
            return redirect('/account/setup-stripe')

        if not current_user.active_subscription:
            current_user.currently_accepting_orders = False
            db.session.commit()

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

        current_time = datetime.datetime.now()
        current_user.most_recent_time_orders_queried = current_time

        if current_time > current_user.next_closing_time:
            current_user.currently_accepting_orders = False
            current_user.next_closing_time = calculate_next_closing_time(current_user.closing_times)
        
        db.session.commit()

        currently_accepting_orders = "true" if current_user.currently_accepting_orders else "false"

        return render_template('view-orders.html', pending_orders=pending_orders, archived_orders=archived_orders, currently_accepting_orders=currently_accepting_orders, order_url=current_user.order_url)
    else:
        return redirect('/login')

# POST endpoint for getting an updated order list without refreshing the page
@account.route('/account/get-updated-orders', methods=['POST'])
def get_updated_orders():
    if current_user.is_authenticated:

        if not current_user.active_subscription:
            current_user.currently_accepting_orders = False
            db.session.commit()
        
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

        current_time = datetime.datetime.now()
        current_user.most_recent_time_orders_queried = current_time

        if current_time > current_user.next_closing_time:
            current_user.currently_accepting_orders = False
            current_user.next_closing_time = calculate_next_closing_time(current_user.closing_times)
        
        db.session.commit()

        currently_accepting_orders = "true" if current_user.currently_accepting_orders else "false"
 
        return jsonify([pending_orders, archived_orders, currently_accepting_orders])
    else:
        return redirect('/login')

# POST endpoint for toggling currently_accepting_orders
@account.route('/account/update-accepting-orders-status', methods=['POST'])
def update_accepting_orders_status():
    if current_user.is_authenticated:
        if not current_user.active_subscription:
            return "not accepting orders"

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

        restaurant_name = json.loads(User.query.filter_by(order_url=order.order_url).first().account_details)['restaurant_name']

        send_order_refunded_email(order.customer_email, rejection_description, order.customer_name, restaurant_name)

        return "success"
    else:
        return "failure"

# MARK: admin

def get_admin_page():
    users_without_urls = User.query.filter_by(order_url=None)
    users = []
    for userObject in users_without_urls:
        user = {}
        user['email_address'] = userObject.email_address
        user['active_subscription'] = userObject.active_subscription
        user['stripe_charges_enabled'] = userObject.stripe_charges_enabled
        user['paid_for_hardware'] = userObject.paid_for_hardware
        user['paid_for_website'] = userObject.paid_for_website
        user['shipping_address'] = userObject.shipping_address
        user['account_details'] = userObject.account_details
        user['menu_notes'] = userObject.menu_notes
        user['order_url'] = userObject.order_url
        user['website_url'] = userObject.website_url
        users.append(user)

    users_with_urls = User.query.filter(User.order_url.isnot(None))
    users_with = []
    for userObject in users_with_urls:
        user = {}
        user['email_address'] = userObject.email_address
        user['active_subscription'] = userObject.active_subscription
        user['stripe_charges_enabled'] = userObject.stripe_charges_enabled
        user['paid_for_hardware'] = userObject.paid_for_hardware
        user['paid_for_website'] = userObject.paid_for_website
        user['shipping_address'] = userObject.shipping_address
        user['account_details'] = userObject.account_details
        user['menu_notes'] = userObject.menu_notes
        user['order_url'] = userObject.order_url
        user['website_url'] = userObject.website_url
        users_with.append(user)

    return render_template('admin.html', users_without_urls=json.dumps(users), users_with_urls=json.dumps(users_with))

@account.route('/account/admin-download-database')
def admin_download_database():
    if current_user.is_authenticated and current_user.email_address == env['admin_username']:
        return send_file("database.db", as_attachment=True)
    else:
        abort(404)

@account.route('/account/admin-download-menu-file', methods=['POST'])
def admin_download_menu_file():
    if current_user.is_authenticated and current_user.email_address == env['admin_username']:
        user =  User.query.filter_by(email_address=request.form['email_address']).first()
        menu_file = user.menu_file
        menu_file_filename = user.menu_file_filename
        if menu_file:
            return send_file(io.BytesIO(menu_file), as_attachment=True, attachment_filename=menu_file_filename)
        return ('', 204) # do nothing
    else:
        abort(404)

@account.route('/account/admin-assign-order-url-to-account', methods=['POST'])
def admin_assign_order_url_to_account():
    if current_user.is_authenticated and current_user.email_address == env['admin_username']:
        account_email = request.form['email_address']
        account_url = request.form['url']
        user = User.query.filter_by(email_address=account_email).first()
        user.order_url = account_url
        db.session.commit()
        return redirect('/account')
    else:
        abort(404)

@account.route('/account/admin-assign-website-url-to-account', methods=['POST'])
def admin_assign_website_url_to_account():
    if current_user.is_authenticated and current_user.email_address == env['admin_username']:
        account_email = request.form['email_address']
        website_url = request.form['url']
        user = User.query.filter_by(email_address=account_email).first()
        user.website_url = website_url
        db.session.commit()
        return redirect('/account')
    else:
        abort(404)

# MARK: functions
def is_valid_setup_account_details_post_request(request):
    if request.form:
        if ('name' in request.form) and ('email' in request.form) and ('phone' in request.form) and ('restaurant_name' in request.form) and ('restaurant_address' in request.form):
            if ('menu_url' in request.form) or ('menu_file' in request.files):
                return True
    return False

def is_valid_edit_account_details_post_request(request):
    if request.form:
        if ('name' in request.form) and ('email' in request.form) and ('phone' in request.form):
            if ('menu_url' in request.form) or ('menu_file' in request.files):
                return True
    return False


def is_valid_menu_notes_post_request(request):
    if request.form:
        if 'menu_notes' in request.form:
            return True
    return False

def is_valid_closing_times_post_request(request):
    if request.form:
        if 'closing_times' in request.form:
            for closing_time in json.loads(request.form['closing_times']):
                if ('minute' not in closing_time) or ('hour' not in closing_time) or ('day' not in closing_time) or ('timezone' not in closing_time):
                    return False
                if (type(closing_time['minute']) != int) or (type(closing_time['hour']) != int) or (type(closing_time['day']) != int):
                    return False
                if (closing_time['minute'] < 0) or (closing_time['minute'] > 60) or (closing_time['hour'] < 0) or (closing_time['hour'] > 23) or (closing_time['day'] < 0) or (closing_time['day'] > 6):
                    return False

                tz_options = ['US/Alaska', 'US/Aleutian', 'US/Arizona', 'US/Central', 'US/East-Indiana', 'US/Eastern', 'US/Hawaii', 'US/Indiana-Starke', 'US/Michigan', 'US/Mountain', 'US/Pacific', 'US/Samoa']
                if closing_time['timezone'] not in tz_options:
                    return False
                
                return True
    return False


def calculate_next_closing_time(closing_times):
    current_time = datetime.datetime.now().replace(second=0, microsecond=0)

    next_closing_times = []

    # closing_time is a json string containing a list of dicts: {"day": 0-6, "hour": 0-60, "minute": 0-60, "timezone": "US/Alaska"}
    for closing_time in json.loads(closing_times):

        current_time_in_new_tz = current_time.astimezone(pytz.timezone(closing_time['timezone']))
        next_closing_time = current_time_in_new_tz

        while next_closing_time.minute != closing_time['minute']:
            next_closing_time += datetime.timedelta(minutes=1)
        while next_closing_time.hour != closing_time['hour']:
            next_closing_time += datetime.timedelta(hours=1)
        while next_closing_time.weekday() != closing_time['day']:
            next_closing_time += datetime.timedelta(1)

        next_closing_times.append(next_closing_time)

    if len(next_closing_times) == 0:
        return datetime.datetime.max
    else:
        return min(next_closing_times)

def convertTimeToSpecificTimezone(time, timezone):
    return timezone.localize(datetime.combine(datetime.today(), t)).timetz()

def send_order_refunded_email(customer_email, rejection_description, customer_name, restaurant_name):
    msg = Message(subject='Order Could Not be Fulfilled', sender=env['email_sender_address'], recipients=[customer_email])
    msg.html = render_template('order-rejected-email.html', rejection_description=rejection_description, customer_name=customer_name, restaurant_name=restaurant_name)
    mail.send(msg)
