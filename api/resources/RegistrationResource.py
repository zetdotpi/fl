import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import falcon

from models import User, Client, OrganisationInfo, RegistrationToken
from models.utils import generate_token


class RegistrationResource:
    def on_post(self, req, resp):
        email = req.params.get('email')

        if req.params.get('abirvalg', None) == 'on':
            print('HONEYPOT abirvalg! possible bot')
            raise falcon.HTTPForbidden()

        if req.params.get('pwdInput') is not None:
            print('HONEYPOT pwdInput is not empty. possible bot')
            raise falcon.HTTPForbidden()

        if User.select().where(User.login == email).count() > 0:
            print('{} already exist. Redirecting to app'.format(email))
            raise falcon.HTTPFound('https://app.example.com')

        token = generate_token()
        current_tokens = [tok.value for tok in RegistrationToken.select()]
        while token in current_tokens:
            token = generate_token()

        client = Client(contact_email=email)
        client.save()

        org_info = OrganisationInfo()
        org_info.save()

        new_user = User(login=email, pwd_hash='prereg', client_profile=client, organisation_info=org_info)
        new_user.save()

        regtoken = RegistrationToken(value=token, user=new_user)
        regtoken.save()

        reg_link = 'https://app.example.com/registration/profile?reg_token={0}'.format(regtoken.value)
        recipient = email
        subject = 'Регистрация Example'

        text = '''Добрый день.
        Для подтверждения адреса электропочты и окончания регистрации пройдите по ссылке ниже.
        {0}
        '''.format(reg_link)

        html = '''<html><body>
        <p><b>Добрый день.<b></p>
        <p>Для подтверждения адреса электронной почты и окончания регистрации щелкните <a href="{0}">сюда</a> или пройдите по ссылке ниже.</p>
        <p><a href="{0}">{0}</a></p>
        </body></html>
        '''.format(reg_link)

        _send_email(recipient, subject=subject, text=text, html=html)
        raise falcon.HTTPFound('https://app.example.com/registration/confirm')


def _send_email(to, subject, text, html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Регистрация Example'
    msg['From'] = 'Example mailbot <bot@example.com>'
    msg['To'] = to
    if text is not None:
        msg.attach(MIMEText(text, 'plain'))
    if html is not None:
        msg.attach(MIMEText(html, 'html'))

    s = smtplib.SMTP('localhost')
    # s.starttls()
    s.sendmail(msg['From'], to, msg.as_string())
    s.quit()
