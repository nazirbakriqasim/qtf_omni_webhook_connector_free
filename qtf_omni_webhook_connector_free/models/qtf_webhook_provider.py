# -*- coding: utf-8 -*-
import requests
import json
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class QtfWebhookProvider(models.Model):
    _name = 'qtf.webhook.provider'
    _description = 'Universal Webhook Alert Provider (QTF Free)'

    qtf_name = fields.Char(string='Endpoint Name', required=True, default='My Messaging Gateway')
    qtf_api_url = fields.Char(string='API Endpoint URL', required=True,
                              help="The full URL to send the POST request to.")

    qtf_headers_json = fields.Text(
        string='HTTP Headers (JSON)',
        default='{\n  "Content-Type": "application/json"\n}',
        help="Specify HTTP headers in JSON format."
    )

    qtf_payload_template = fields.Text(
        string='Payload Template (JSON)',
        default='{\n  "chatId": "{{chatId}}",\n  "message": "{{message}}"\n}',
        help="Use {{chatId}} for dynamic recipient phone and {{message}} for the chat text."
    )
    qtf_active_provider = fields.Boolean(string='Active', default=True)

    # Core relationship fields linking Odoo users to their specific chat devices
    qtf_user_id = fields.Many2one('res.users', string='Odoo User', required=True,
                                  help="The user who will receive notifications.")
    qtf_recipient_chat_id = fields.Char(string='Recipient Chat ID / Phone', required=True,
                                        placeholder="e.g. 963933135037@c.us")

    def qtf_send_dynamic_alert(self, target_chat_id, clean_message):
        """ Dispatches dynamic payload requests directly to the specific user's device """
        for record in self:
            if not record.qtf_active_provider or not record.qtf_api_url:
                continue

            headers = {'Content-Type': 'application/json'}
            if record.qtf_headers_json:
                try:
                    headers = json.loads(record.qtf_headers_json)
                except Exception:
                    pass

            payload_data = {
                "chatId": target_chat_id,
                "message": clean_message
            }

            if record.qtf_payload_template:
                try:
                    escaped_message = json.dumps(clean_message)[1:-1]
                    raw_payload_str = record.qtf_payload_template.replace('{{chatId}}', target_chat_id).replace(
                        '{{message}}', escaped_message)
                    payload_data = json.loads(raw_payload_str)
                except Exception:
                    pass

            try:
                response = requests.post(record.qtf_api_url, json=payload_data, headers=headers, timeout=15,
                                         verify=False)
                _logger.info("QTF Outbound Connection Success Log - Status: %s - Content: %s", response.status_code,
                             response.text)
            except Exception as e:
                _logger.error("QTF Severe Outbound Network Connection Fault: %s", e)

    def qtf_action_test_api_connection(self):
        """ Hardened test action executing direct non-conditional delivery """
        for record in self:
            # Formulate an explicit test payload fetching the dynamic chat ID straight from the view context
            target_phone = record.qtf_recipient_chat_id or "963933135037@c.us"
            test_url = record.qtf_api_url

            if not test_url:
                return record._qtf_show_notification('Error ❌', 'Please specify an API endpoint URL.', 'danger')

            headers = {'Content-Type': 'application/json'}
            if record.qtf_headers_json:
                try:
                    headers = json.loads(record.qtf_headers_json)
                except Exception:
                    pass

            test_payload = {
                "chatId": target_phone,
                "message": "Live targeted user alert routing verification successful! 🚀"
            }

            try:
                # Dispatch outbound API connection straight from button callback to bypass system message hooks context
                response = requests.post(test_url, json=test_payload, headers=headers, timeout=15, verify=False)
                _logger.info("QTF Instant Button Live Response - Status: %s - Content: %s", response.status_code,
                             response.text)
                return record._qtf_show_notification('Connection Fired 🎉',
                                                     'Payload transmitted directly. Check your device!', 'success')
            except Exception as e:
                return record._qtf_show_notification('Interface Fault ❌', str(e), 'danger')

    def _qtf_show_notification(self, title, message, notify_type):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': notify_type,
                'sticky': False,
            }
        }
