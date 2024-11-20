from odoo import models, fields, api


class StkResponse(models.Model):
    _name = 'safaricom_stk.stk_response'
    _description = 'Safaricom STK Response'

    name = fields.Char(related="checkout_request_id", readonly=True)
    merchant_request_id = fields.Char(string="Merchant Request ID", readonly=True)
    checkout_request_id = fields.Char(string="Checkout Request ID", readonly=True)
    response_code = fields.Char(string="Response Code", readonly=True)
    response_description = fields.Char(string="Response Description", readonly=True)
    customer_message = fields.Char(string="Customer Message", readonly=True)
    stk_request_id = fields.Many2one('safaricom_stk.stk_request', string='STK Request', readonly=True)
