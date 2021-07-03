from flask import Blueprint, render_template

order = Blueprint('order', __name__)

@order.route('/super-cucas-micheltorena')
def super_cucas_micheltorena():
    return render_template('super-cucas-micheltorena.html')
