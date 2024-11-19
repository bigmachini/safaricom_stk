from odoo import models, fields, api
from datetime import datetime


class STKCallback(models.Model):
    _name = 'safaricom_stk.stk_callback'
    _description = 'Safaricom STK Callback'

    name = fields.Char(string='Name', required=True)
    merchant_request_id = fields.Char(string='Merchant Request ID')
    checkout_request_id = fields.Char(string='Checkout Request ID')
    result_code = fields.Integer(string='Result Code')
    result_desc = fields.Char(string='Result Description')
    amount = fields.Float(string='Amount')
    mpesa_receipt_number = fields.Char(string='Mpesa Receipt Number')
    transaction_date = fields.Datetime(string='Transaction Date')
    phone_number = fields.Char(string='Phone Number')
    stk_response_id = fields.Many2one('safaricom_stk.stk_response', string='STK Response')
    stk_request_id = fields.Many2one(related='stk_response_id.stk_request_id', string='STK Request')


    @api.model
    def create_from_json(self, data):
        callback_data = data.get('Body', {}).get('stkCallback', {})
        callback_metadata = callback_data.get('CallbackMetadata', {}).get('Item', [])

        # Extracting metadata items
        metadata = {item['Name']: item.get('Value') for item in callback_metadata}

        merchant_request_id = callback_data.get('MerchantRequestID', '')
        checkout_request_id = callback_data.get('CheckoutRequestID', '')
        stk_response = self.env['safaricom_stk.stk_response'].search(
            ['|', ('merchant_request_id', '=', merchant_request_id),
             ('checkout_request_id', '=', checkout_request_id)], limit=1)

        # Creating the record
        vals = {
            'stk_response_id': stk_response.id,
            'name': callback_data.get('MerchantRequestID', ''),
            'merchant_request_id': merchant_request_id,
            'checkout_request_id': checkout_request_id,
            'result_code': callback_data.get('ResultCode', 0),
            'result_desc': callback_data.get('ResultDesc', ''),
            'amount': metadata.get('Amount', 0.0),
            'mpesa_receipt_number': metadata.get('MpesaReceiptNumber', ''),
            'transaction_date': datetime.strptime(str(metadata.get('TransactionDate', '')),
                                                  '%Y%m%d%H%M%S') if metadata.get('TransactionDate') else False,
            'phone_number': metadata.get('PhoneNumber', '')
        }
        self.create([vals])
