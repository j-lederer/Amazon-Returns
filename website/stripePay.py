from flask import Flask, render_template, url_for, request, abort, Blueprint, flash

import stripe
from . import db
import os

#from . import app
#stripe.api_key = app.config['STRIPE_SECRET_KEY']

stripePay = Blueprint('stripePay', __name__)



@stripePay.route('/stripeHome')
def index():
    '''
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1GtKWtIdX0gthvYPm4fJgrOr',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    '''
    return render_template(
        'index.html', 
        #checkout_session_id=session['id'], 
        #checkout_public_key=app.config['STRIPE_PUBLIC_KEY']
    )

@stripePay.route('/stripe_pay')
def stripe_pay():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1NQ4URGx5rHp5dcp9EAHb1bs',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('stripePay.thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('stripePay.index', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': os.environ['STRIPE_TEST_PUBLIC_KEY']
      #app.config['STRIPE_PUBLIC_KEY']
    }

@stripePay.route('/thanks')
def thanks():
    return render_template('thanks.html')

@stripePay.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'YOUR_ENDPOINT_SECRET'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    print(event)
    print(event['type'])
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])
        print('test')

    return {}
