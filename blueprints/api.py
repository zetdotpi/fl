import string
from datetime import datetime
from random import choice
import phonenumbers
from flask import Blueprint, request, jsonify, redirect
from models import *
from models.utils import generate_token
from utils import dbg_print, send_email, send_sms

api = Blueprint('api', __name__, url_prefix='/api', template_folder='templates')


@api.route('/svc/sendmail/', methods=['POST'])
def sendmail():
    json = request.get_json()

    subject = json['subj']
    text = json['message']

    send_email('info@it-citrus.ru', subject=subject, text=text)
    return '1'


@api.route('/login/check/', methods=['POST'])
def check_login():
    json = request.get_json()
    social_network = json['social']['network']
    social_id = json['social']['id']

    social = SocialDetails.select().where(
        SocialDetails.net_name == social_network,
        SocialDetails.net_id == social_id)
    if social.count() > 0:
        records = LoginRecord.select.where(LoginRecord.social == social)
        if records.count() > 0:
            record = records[0]
            data = {
                'result': 'ok',
                'username': social.net_id,
                'password': record.access_token
            }
    else:
        data = {
            'result': 'no login'
        }
    return jsonify(data)


@api.route('/login/', methods=['POST'])
def login():
    json = request.get_json()
    social_network = json['social']['network']
    social_id = json['social']['id']
    action_type = json['action']['type']
    action_id = json['action']['id']

    lr = LoginRecord(
        net_name=social_network,
        net_id=social_id,
        net_action_type=action_type,
        net_action_id=action_id,
        access_token=generate_token()
    )
    lr.save()

    data = {
        'result': 'ok',
        'username': lr.net_id,
        'password': lr.access_token
    }

    return jsonify(data)


@api.route('/log/', methods=['POST'])
def put_log():
    json = request.get_json()

    dbg_print('json', json)
    dbg_print('request.user_agent', request.user_agent)
    dbg_print('request.remote_addr', request.remote_addr)

    hotspot_name = json['hotspot_name']

    method = json['method']     # login method, `social` or `phone`
    if method == 'social':
        social_network = json['social']['network']
        social_id = json['social']['id']
        social_first_name = json['social']['first_name']
        social_second_name = json['social']['second_name']

        with database.atomic() as txn:
            try:
                if SocialDetails.select().where(
                    SocialDetails.net_name == social_network,
                    SocialDetails.net_id == social_id
                ).count() > 0:
                    social = SocialDetails.get(
                        SocialDetails.net_name == social_network,
                        SocialDetails.net_id == social_id
                    )
                else:
                    social = SocialDetails(
                        net_name=social_network,
                        net_id=social_id,
                        name=social_first_name,
                        surname=social_second_name
                    )
                    social.save()

                lr = LoginRecord(
                    hotspot=Hotspot.get(Hotspot.name == hotspot_name),
                    method=method,
                    social=social,
                    access_token=generate_token(),

                    ua_browser=request.user_agent.browser,
                    ua_platform=request.user_agent.platform,
                    ua_string=request.user_agent.string,
                    ua_version=request.user_agent.version
                )
                lr.save()
                data = {'result': 'ok'}
            except Hotspot.DoesNotExist:
                print('Hotspot with name {0} not found.'.format(hotspot_name))
                txn.rollback()
                data = {'result': 'error'}
            except:
                print('Something went terribly wrong!')
                txn.rollback()
                data = {'result': 'error'}

    elif method == 'phone':
        phone = json['phone']
        lr = LoginRecord(
            hotspot=Hotspot.get(Hotspot.name == hotspot_name),
            method=method,
            phone=phone,
            access_token=generate_token()
        )
        lr.save()
        data = {'result': 'ok'}
    else:
        data = {'result': 'error'}

    return jsonify(data)


@api.route('/get_post/', methods=['POST'])
def get_post():
    json = request.get_json()
    hotspot_name = json['hotspot_name']
    social = json['social_network']

    try:
        hotspot = Hotspot.get(Hotspot.name == hotspot_name)
    except Hotspot.DoesNotExist:
        print('Hotspot with name {0} not found.'.format(hotspot_name))
        data = {'result': 'error'}

    if social == 'vk':
        if hotspot.publications_vk.count() > 0:
            publication = hotspot.publications_vk[0]
            data = {
                'result': 'ok',
                'text': publication.text,
                'image': publication.image.vk_id() if publication.image is not None else None
            }
        else:
            data = {
                'result': 'use defaults'
            }

    return jsonify(data)


@api.route('/sms/get/', methods=['POST'])
def get_sms():
    sms_chars = string.digits
    json = request.get_json()
    hotspot_name = json['hotspot_name']
    phonenum = json['phone']

    try:
        hotspot = Hotspot.get(Hotspot.name == hotspot_name)
    except Hotspot.DoesNotExist:
        print('Hotspot with name {0} not found.'.format(hotspot_name))
        data = {'result': 'error'}
    else:
        if hotspot.paid_until is None or hotspot.paid_until < date.today():
            data = {'result': 'sms not available'}
        else:
            try:
                token_length = 4
                phone = phonenumbers.parse(phonenum)

                current_tokens = [token.value for token in SMSLoginToken.select()]
                token = ''.join([choice(sms_chars) for _ in range(token_length)])
                while token in current_tokens:
                    token = ''.join([choice(sms_chars) for _ in range(token_length)])

                smstoken = SMSLoginToken(
                    hotspot=hotspot,
                    phone=str(phone.country_code) + str(phone.national_number),
                    value=token
                )
                smstoken.save()
                msgtext = '''Ваш код для доступа к WiFi
                {0}'''.format(smstoken.value)

                send_sms(phone, msgtext)
                data = {'result': 'ok'}
            except phonenumbers.NumberParseException:
                data = {'result': 'error'}

    return jsonify(data)


@api.route('/sms/login/', methods=['POST'])
def login_with_sms():
    json = request.get_json()
    hotspot_name = json['hotspot_name']
    smscode = json['smscode']

    data = {'result': 'error'}
    try:
        hotspot = Hotspot.get(Hotspot.name == hotspot_name)
    except Hotspot.DoesNotExist:
        print('Hotspot with name {0} not found.'.format(hotspot_name))
        data = {'result': 'error'}

    try:
        token = SMSLoginToken.get(SMSLoginToken.value == smscode)
        with database.atomic() as txn:
            lr = LoginRecord(
                hotspot=Hotspot.get(Hotspot.name == hotspot_name),
                method='phone',
                access_token=token.value,
                ua_browser=request.user_agent.browser,
                ua_platform=request.user_agent.platform,
                ua_string=request.user_agent.string,
                ua_version=request.user_agent.version
            )
            lr.save()
            token.delete_instance()
            data = {'result': 'ok'}

    except SMSLoginToken.DoesNotExist:
        print('No SMS token found')
        data = {'result': 'error'}

    finally:
        return jsonify(data)


@api.route('/call_me', methods=['POST'])
def call_me():
    name = request.form['name'] if 'name' in request.form.keys() else 'Anonymous'
    phone = request.form['phone'] if 'phone' in request.form.keys() else None
    email = request.form['email'] if 'email' in request.form.keys() else None
    note = request.form['note'] if 'note' in request.form.keys() else None

    subject = '[Example] {0} заказал перезвон.'.format(name)
    recipient = 'mail@example.com'
    text = '''Имя: {0}
    Телефон: {1}
    email: {2}
    Заметка: {3}
    --------------------------------------
    время заказа звонка {4}
    '''.format(
        name,
        phone,
        email,
        note,
        datetime.now()
    )
    html = '''
    <html>
        <body>
            <h1>Надо позвонить потенциальному клиенту</h1>
            <p>Имя: {0}</p>
            <p>Телефон: {1}</p>
            <p>email: {2}</p>
            <p>Заметка: {3}</p>
            <hr>
            <p>время заказа звонка {4}</p>
        </body>
    </html>
    '''.format(
        name,
        phone,
        email,
        note,
        datetime.now()
    )

    send_email(recipient, subject=subject, text=text, html=html)
    return redirect('http://example.com', code=302)


@api.route('/special_offer', methods=['POST'])
def special_offer():
    email = request.form['phone'] if 'phone' in request.form.keys() else None
    offer = request.form['offer'] if 'offer' in request.form.keys() else False
    wants_mail = request.form['wants_mail'] if 'wants_mail' in request.form.keys else False

    subject = '[Example] заказ спецпредложения.'
    recipient = 'info@it-citrus.ru'
    text = '''email: {0}
    Хочет спецпредложение: {1}
    Хочет получать рассылку: {2}
    --------------------------------------
    время заказа звонка {3}
    '''.format(
        email,
        offer,
        wants_mail,
        datetime.now()
    )
    html = '''<html>
        <body>
            <h1>Клиент хочет спецпредложение.</h1>
            <p>email: {0}</p>
            <p>Хочет спецпредложение: {1}</p>
            <p>Хочет получать рассылку: {2}</p>
            <hr>
            <p>время заказа звонка {3}</p>
        </body>
    </html>
    '''.format(
        email,
        offer,
        wants_mail,
        datetime.now()
    )

    send_email(recipient, subject=subject, text=text, html=html)
    return redirect('http://example.com', code=302)
