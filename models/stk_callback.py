from odoo import models, fields, api
from datetime import datetime


class STKCallback(models.Model):
    _name = 'safaricom_stk.stk_callback'
    _description = 'Safaricom STK Callback'

    name = fields.Char(related="mpesa_receipt_number", readonly=True)
    merchant_request_id = fields.Char(string='Merchant Request ID', readonly=True)
    checkout_request_id = fields.Char(string='Checkout Request ID', readonly=True)
    result_code = fields.Integer(string='Result Code', readonly=True)
    result_desc = fields.Char(string='Result Description', readonly=True)
    amount = fields.Float(string='Amount', readonly=True)
    mpesa_receipt_number = fields.Char(string='Mpesa Receipt Number', readonly=True)
    transaction_date = fields.Datetime(string='Transaction Date', readonly=True)
    phone_number = fields.Char(string='Phone Number', readonly=True)
    stk_response_id = fields.Many2one('safaricom_stk.stk_response', string='STK Response', readonly=True)
    stk_request_id = fields.Many2one(related='stk_response_id.stk_request_id', string='STK Request', readonly=True)

    @api.model
    def create_from_json(self, data):
        callback_data = data.get('Body', {}).get('stkCallback', {})
        callback_metadata = callback_data.get('CallbackMetadata', {}).get('Item', [])

        # Extracting metadata items
        metadata = {item['Name']: item.get('Value') for item in callback_metadata}

        merchant_request_id = callback_data.get('MerchantRequestID', '')
        checkout_request_id = callback_data.get('CheckoutRequestID', '')

        stk_callback = self.env['safaricom_stk.stk_callback'].search(
            ['|', ('merchant_request_id', '=', merchant_request_id),
             ('checkout_request_id', '=', checkout_request_id)], limit=1)
        if not stk_callback:
            stk_response = self.env['safaricom_stk.stk_response'].search(
                ['|', ('merchant_request_id', '=', merchant_request_id),
                 ('checkout_request_id', '=', checkout_request_id)], limit=1)

            result_code = callback_data.get('ResultCode', None)
            if result_code == 0:
                stk_response.stk_request_id.transaction_status = 'completed'
            else:
                stk_response.stk_request_id.transaction_status = 'failed'

            # Creating the record
            vals = {
                'stk_response_id': stk_response.id,
                'name': callback_data.get('MerchantRequestID', ''),
                'merchant_request_id': merchant_request_id,
                'checkout_request_id': checkout_request_id,
                'result_code': result_code,
                'result_desc': callback_data.get('ResultDesc', ''),
                'amount': metadata.get('Amount', 0.0),
                'mpesa_receipt_number': metadata.get('MpesaReceiptNumber', ''),
                'transaction_date': datetime.strptime(str(metadata.get('TransactionDate', '')),
                                                      '%Y%m%d%H%M%S') if metadata.get('TransactionDate') else False,
                'phone_number': metadata.get('PhoneNumber', '')
            }
            return self.create([vals])
