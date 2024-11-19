# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.http import request

HEADERS = [('Content-Type', 'application/json'),
           ('Cache-Control', 'no-store')]


class SafaricomStk(http.Controller):
    @http.route('/api/stk/callback', auth='public', methods=['POST'], csrf=False)
    def api_stk_callback(self, **kw):
        logging.info(f'SafaricomStk::api_stk_callback::')

        data = json.loads(request.httprequest.data)
        logging.info(f'SafaricomStk::api_stk_callback:: data --> {data}')

        try:
            stk_callback = request.env['safaricom_stk.stk_callback'].sudo().create_from_json(data)
            logging.info(f'SafaricomStk::api_stk_callback:: stk_callback --> {stk_callback}')

            response = {
                'status': True,
                'message': '',
                'data': {}
            }
            return request.make_response(json.dumps(response), HEADERS, status=400)
        except Exception as ex:
            response = {
                'status': False,
                'message': 'Invalid MAC address format',
                'data': {}
            }
            return request.make_response(json.dumps(response), HEADERS, status=400)
