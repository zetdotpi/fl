import json
import os
import base64
from datetime import date, timedelta
import urllib.parse
from flask import Flask, request, make_response, render_template, flash, redirect, url_for, abort
import phonenumbers
import pika
from pprint import pprint
from models import *
from utils import dict_to_state, state_to_dict
import config


debug_mode = config.DEBUG

hs = Flask(__name__)
hs.config.from_pyfile('hs_config.py')


def mq_send_msg(channel, data):
    if channel not in ['ig', 'vk', 'fb', 'ok']:
        raise Exception('channel not supported')

    credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
    conn_params = pika.ConnectionParameters(config.RABBITMQ_HOST, config.RABBITMQ_PORT, config.RABBITMQ_VHOST, credentials)
    with pika.BlockingConnection(conn_params) as connection:
    
        ch = connection.channel()
        ch.queue_declare('channel')

        ch.basic_publish('', channel, data)


# LOCALIZATION UTILS
def _get_lang():
    supported_langs = ['en', 'ru']

    if request.args.get('lang') in supported_langs:
        return request.args.get('lang')

    return request.accept_languages.best_match(supported_langs)


def _get_localized_template(hotspot, template_variant, template_name, **kwargs):
    if hotspot.preferred_language == 'auto':
        lang = kwargs.get('lang')
        if lang is None:
            lang = _get_lang() or 'en'
    else:
        lang = hotspot.preferred_language

    return os.path.join('hotspot', template_variant, lang, template_name)


def _localized_redirect(request, endpoint, **kwargs):
    pass


@hs.before_request
def db_connect():
    database.connect()


@hs.after_request
def db_close(response):
    if not database.is_closed():
        print('Closing database connection')
        database.close()
    return response


@hs.teardown_request
def teardown(exception):
    if exception is not None:
        print("=== REQUEST TEARDOWN INITIATED ===")
        print(exception)
        if not database.is_closed():
            database.close()


@hs.route('/agreement/')
def agreement():
    lang = _get_lang()
    if lang == 'ru':
        return render_template('hotspot/agreement.html')
    return render_template('hotspot/en_agreement.html')


@hs.route('/')
def main():
    identity = request.args.get('identity')
    target = request.args.get('target')
    mac = request.args.get('mac')
    preview = 'preview' in request.args

    if preview:
        print('Preview mode')

    try:
        hotspot = Hotspot.get(Hotspot.identity == identity)

        # Display preview without checking anything
        if preview:
            return redirect(url_for('call_phone_form', identity=identity, preview=True))

        if hotspot.paid_until is None or hotspot.paid_until < date.today():
            return redirect(url_for('auth_not_available', identity=identity))

        # looking for MAC in our database
        mac_phone_pair = HS_mac_phone_pair.get(HS_mac_phone_pair.mac == mac)
        if mac_phone_pair.is_valid():
            return redirect(url_for('login_successful', mac=mac, target=target, identity=identity))
        else:
            if not mac_phone_pair.is_fresh():
                mac_phone_pair.delete_instance()

    except Hotspot.DoesNotExist:
        abort(400)
    except HS_mac_phone_pair.DoesNotExist:
        return redirect(url_for('call_phone_form', identity=identity, mac=mac, target=target))

    return redirect(url_for('call_phone_form', identity=identity, mac=mac, target=target))


@hs.route('/login/call/', methods=['GET', 'POST'])
def call_phone_form():
    identity = request.args.get('identity')
    target = request.args.get('target')
    mac = request.args.get('mac')
    preview = request.args.get('preview', False)
    if identity is None:
        abort(400)
    try:
        hotspot = Hotspot.get(Hotspot.identity == identity)
    except Hotspot.DoesNotExist:
        abort(400)

    if preview:
        return render_template(
            _get_localized_template(hotspot, 'v2', 'phone/form.html'),
            hotspot=hotspot, preview=True
        )

    if hotspot.paid_until is None or hotspot.paid_until < date.today():
        return redirect(url_for('auth_not_available', identity=identity))

    if request.method == 'POST':
        phonenumber = request.form['phone']
        print(phonenumber)

        try:
            phone = phonenumbers.parse(phonenumber)
            phone_string = '{}{}'.format(phone.country_code, phone.national_number)

            with database.atomic():
                print('In atomic mode')
                if HS_mac_phone_pair.select().where(HS_mac_phone_pair.mac == mac).count() > 0:
                    # delete matching by mac HS_mac_phone_pair before inserting new
                    deleted_count = HS_mac_phone_pair.delete().where(HS_mac_phone_pair.mac == mac).execute()
                    print('Deleted {} entries'.format(deleted_count))

                pair = HS_mac_phone_pair(
                    mac=mac.upper(),
                    phone=phone_string
                )
                pair.save(force_insert=True)
                print('Atomic mode finish')

        except phonenumbers.NumberParseException:
            flash('Вы ввели неправильный номер телефона')
            return render_template(
                _get_localized_template(hotspot, 'v2', 'phone/form.html'),
                hotspot=hotspot, target=target, mac=mac)

        except IntegrityError as e:
            print('Duplicate key')
            print(e)
            database.rollback()

        return redirect(url_for('call_submit', identity=identity, mac=mac, target=target))

    return render_template(
        _get_localized_template(hotspot, 'v2', 'phone/form.html'),
        hotspot=hotspot, target=target, mac=mac)


@hs.route('/login/call/submit')
def call_submit():
    identity = request.args.get('identity')
    target = request.args.get('target')
    mac = request.args.get('mac')

    pair = HS_mac_phone_pair.get(HS_mac_phone_pair.mac == mac.upper())
    phone = pair.phone

    if identity is None:
        abort(400)
    try:
        hotspot = Hotspot.get(Hotspot.identity == identity)
    except Hotspot.DoesNotExist:
        abort(400)

    if hotspot.paid_until is None or hotspot.paid_until < date.today():
        return redirect(url_for('auth_not_available', identity=identity))

    return render_template(
        _get_localized_template(hotspot, 'v2', 'phone/submit.html'),
        hotspot=hotspot)


@hs.route('/check', methods=['GET'])
def check_login():
    mac = request.args.get('mac')
    try:
        pair = HS_mac_phone_pair.get(HS_mac_phone_pair.mac == mac)
        if pair.is_valid():
            resp = make_response('', 200)
            resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            return resp
        else:
            resp = make_response('', 403)
            resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            return resp
    except HS_mac_phone_pair.DoesNotExist:
        resp = make_response('', 403)
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return resp


@hs.route('/login/not_available')
def auth_not_available():
    identity = request.args.get('identity')
    hotspot = Hotspot.get(Hotspot.identity == identity)
    return render_template(_get_localized_template(hotspot, 'v2', 'not_available.html'), hotspot=hotspot)


@hs.route('/login/success/', methods=['GET'])
def login_successful():
    target = request.args.get('target')
    mac = request.args.get('mac')
    identity = request.args.get('identity')

    try:
        hotspot = Hotspot.get(Hotspot.identity == identity)

        # looking for MAC in our database
        mac_phone_pair = HS_mac_phone_pair.get(HS_mac_phone_pair.mac == mac)
        if mac_phone_pair.is_valid():
            # Found.
            # Pasting login record and redirecting to success.
            lr = LoginRecord(
                hotspot=Hotspot.get(Hotspot.name == hotspot.name),
                method='phone',
                phone=mac_phone_pair.phone,
                access_token='',
                ua_browser=request.user_agent.browser,
                ua_platform=request.user_agent.platform,
                ua_string=request.user_agent.string,
                ua_version=request.user_agent.version
            )
            lr.save()

            params = {
                'dst': target or 'https://www.google.com'

            }
            params['username'] = mac

            print('redirecting to {0}'.format('http://hs.example.com/login?' + urllib.parse.urlencode(params)))
            return redirect('http://hs.example.com/login?' + urllib.parse.urlencode(params))
        else:
            mac_phone_pair.delete_instance()
            return redirect(url_for('call_phone_form', identity=identity, target=target, mac=mac))
    except Hotspot.DoesNotExist:
        abort(400)
    except HS_mac_phone_pair.DoesNotExist:
        return redirect(url_for('call_phone_form', identity=identity, mac=mac, target=target))


@hs.route('/social/')
def social_login_page():
    target = request.args.get('target')
    mac = request.args.get('mac')
    identity = request.args.get('identity')
    preview = 'preview' in request.args

    try:
        hotspot = Hotspot.get(Hotspot.identity == identity)
        if preview:
            return render_template(
                _get_localized_template(hotspot, 'v2', 'social_login.html'),
                hotspot=hotspot,
                target=target,
                mac=mac,
                preview=True)
        else:
            return render_template(
                _get_localized_template(hotspot, 'v2', 'social_login.html'),
                hotspot=hotspot,
                target=target,
                mac=mac)
    except Hotspot.DoesNotExist:
        abort(400)


@hs.route('/social/fb')
def fb_callback():
    if 'error' not in request.args:
        mq_send_msg('fb', json.dumps({'code': request.args.get('code')}))
        # TODO: redirect to success
    else:
        print('FB login REJECTED')
    return make_response('', 204)
    

@hs.route('/social/vk')
def vk_callback():
    if 'error' not in request.args:
        mq_send_msg('vk', json.dumps({'code': request.args.get('code')}))
        # TODO: redirect to success
    else:
        print('VK login REJECTED')
    return make_response('', 204)


@hs.route('/social/ok')
def ok_callback():
    if 'error' not in request.args:
        mq_send_msg('ok', json.dumps({'code': request.args.get('code')}))
        # TODO: redirect to success
    else:
        print('OK login REJECTED')
    return make_response('', 204)


if __name__ == '__main__':
    hs.run(debug=True, host='0.0.0.0', port=5001)
