import json
import logging
import uuid

import requests

from .config import stk_push_url, stk_push_call_back_url, mpesa_url_v1

from odoo import models, fields, api


class STKRequest(models.Model):
    _name = 'safaricom_stk.stk_request'
    _description = 'STK Request'

    name = fields.Char(string='UUID', readonly=True, default=lambda self: str(uuid.uuid4()))
    phone_number = fields.Char(string='Phone Number', readonly=True)
    amount = fields.Float(string='Amount', readonly=True)
    till_id = fields.Many2one('safaricom_stk.till', string='Till', readonly=True)
    stk_response_ids = fields.One2many('safaricom_stk.stk_response', 'stk_request_id', string='STK Responses')

    def process_stk_push(self):
        passwd, timestamp = self.till_id.get_password()
        mpesa_auth_token = self.till_id.get_auth()
        access_token = mpesa_auth_token.get('access_token', None)
        headers = {"Authorization": "Bearer %s" % access_token}
        data = {
            "BusinessShortCode": self.till_id.business_short_code,
            "Password": passwd,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": self.amount,
            "PartyA": self.phone_number,
            "PartyB": self.till_id.party_b,
            "PhoneNumber": self.phone_number,
            "CallBackURL": stk_push_call_back_url,
            "AccountReference": "airtime",
            "TransactionDesc": self.phone_number}

        payload = {
            "url": stk_push_url,
            "payload": data,
            "auth": {},
            "headers": headers,
            "method_type": "POST"
        }
        response = requests.request("POST", f'{mpesa_url_v1}/stk_push', headers=headers, json=payload)
        response_text = response.text.replace('\n', '').replace(' ', '')
        logging.info(
            f"STKRequest::process_stk_push  response.status_code {response.status_code}  response.text: {response_text} ")

        if response.status_code == 200:
            stk_response = json.loads(response.text)
            vals = {
                "merchant_request_id": stk_response.get('MerchantRequestID', None),
                "checkout_request_id": stk_response.get('CheckoutRequestID', None),
                "response_code": stk_response.get('ResponseCode', None),
                "response_description": stk_response.get('ResponseDescription', None),
                "customer_message": stk_response.get('CustomerMessage', None),
                "stk_request_id": self.id
            }
            self.env['safaricom_stk.stk_response'].create([vals])
