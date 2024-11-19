import base64
import json
import logging

from odoo import models, fields, api
from .config import mpesa_url_v1
import requests


class Till(models.Model):
    _name = 'safaricom_stk.till'
    _description = 'Safaricom STK Till'

    name = fields.Char(string="Name", required=True)
    consumer_key = fields.Char(string="Consumer Key", required=True)
    consumer_secret = fields.Char(string="Consumer Secret", required=True)
    pass_key = fields.Char(string="Pass Key", required=True)
    business_short_code = fields.Char(string="Business Short Code", required=True)
    initiator_pass = fields.Char(string="Initiator Password", required=True)
    party_b = fields.Char(string="Party B", required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    stk_request_ids = fields.One2many('safaricom_stk.stk_request', 'till_id', string='STK Requests')

    def test_stk_push(self):
        vals = {
            "phone_number": "254753242124",
            "amount": 10,
            "till_id": self.id
        }
        _stk_request = self.env['safaricom_stk.stk_request'].create([vals])
        _stk_request.process_stk_push()

    def get_password(self):
        try:
            from datetime import datetime
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d%H%M%S")
            data_to_encode = f"{self.business_short_code}{self.pass_key}{timestamp}"
            online_password = base64.b64encode(data_to_encode.encode())
            decode_password = online_password.decode('utf-8')
            return decode_password, timestamp
        except Exception as ex:
            logging.exception(ex)
            logging.error(f'get_password Ex: {ex}')

    def get_auth(self):
        try:
            headers = {'Content-Type': 'application/json'}
            url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
            payload = {
                "url": url,
                "payload": {},
                "auth": {'consumer_key': self.consumer_key, 'consumer_secret': self.consumer_secret},
                "headers": headers,
                "method_type": "GET"
            }
            r = requests.post(f'{mpesa_url_v1}/get_auth', data=json.dumps(payload), headers=headers, timeout=30)
            return r.json()
        except Exception as ex:
            logging.exception(ex)
            logging.error(f"get_auth: Ex {ex}")
            return {}
