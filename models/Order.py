import os
from datetime import datetime
from peewee import *

from num2words import num2words
from jinja2 import Environment, FileSystemLoader
import pdfkit

from . import BaseModel, User
import config


class Order(BaseModel):
    client = ForeignKeyField(User, null=True, backref='orders')
    cancelled = BooleanField(default=False)
    paid = BooleanField(default=False)
    enrolled = BooleanField(default=False)

    created_datetime = DateTimeField(default=datetime.now)
    paid_datetime = DateTimeField(null=True)

    def __str__(self):
        return '<Order> [{o.id}] for {o.client.login} with {items_count}'.format(o=self, items_count=self.items.count())

    def freeze(self):
        self.frozen = True
        self.save()

    # States = ['not_paid', 'paid', 'completed', 'cancelled']
    def get_current_status(self):
        if self.paid and self.enrolled:
            return 'completed'
        elif self.paid:
            return 'paid'
        elif self.cancelled:
            return 'cancelled'
        else:
            return 'not_paid'

    def total(self):
        return sum([item.total() for item in self.items])

    def total_in_words(self):
        total = self.total()
        return num2words(total, lang='ru', to='currency', currency='RUB').capitalize()

    def as_dict(self):
        data = {
            'id': self.id,
            'status': self.get_current_status(),
            'created_datetime': self.created_datetime.isoformat(),
            'items': [item.as_dict() for item in self.items],
            'total': sum([item.total() for item in self.items]).to_eng_string(),
            'invoice_pdf_path': self.get_invoice_pdf_path()
        }

        if self.paid_datetime is not None:
            data['paid_datetime'] = self.paid_datetime

        return data

    def get_invoice_pdf_path(self):
        target_folder = os.path.join(os.getcwd(), 'static', 'clients', str(self.client.id), 'invoices')
        if not os.path.exists(target_folder):
                os.makedirs(target_folder)
        target_file_path = os.path.join(target_folder, str(self.id) + '.pdf')

        # finish if file already generated
        if not os.path.exists(target_file_path):
            self.generate_invoice_pdf()

        return '/docs/{0}/invoices/{1}.pdf'.format(self.client.id, self.id)

    def generate_invoice_pdf(self, force=False):
        # prepare paths, etc
        target_folder = os.path.join(os.getcwd(), 'static', 'clients', str(self.client.id), 'invoices')
        if not os.path.exists(target_folder):
                os.makedirs(target_folder)
        target_file_path = os.path.join(target_folder, str(self.id) + '.pdf')

        # finish if file already generated
        if os.path.exists(target_file_path) and not force:
            print(target_file_path + ' already exists. exiting')
            return

        # check if pdf is already present
        env = Environment(
            loader=FileSystemLoader('./docs_templates')
            # autoescape=select_autoescape(['html'])
        )

        template = env.get_template('invoice.html')
        invoice_string = template.render(order=self)

        if hasattr(config, 'WKHTMLTOPDF_PATH'):
            cfg = pdfkit.configuration(wkhtlmtopdf=config.WKHTMLTOPDF_PATH) or None
        else:
            cfg = None
        pdfkit.from_string(
            invoice_string,
            target_file_path,
            configuration=cfg)
