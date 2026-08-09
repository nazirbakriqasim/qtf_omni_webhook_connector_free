# -*- coding: utf-8 -*-
{
    'name': 'Omni Webhook & Messenger Connector (Free) By QTF',
    'version': '19.0.1.0.0',
    'sequence': 10,
    'category': 'Discuss/Marketing',
    'summary': 'Bridge Odoo Discuss Messages with Any Webhook API, Telegram, or WhatsApp Gateways',
    'description': 'A completely free, open-source universal webhook engine developed by QTF to forward Odoo 19 internal chat messages to any messaging gateway or API endpoint dynamically.',
    'author': 'Nazir Bakri Qasim',
    'website': 'https://wa.me/nazirbakriqasim',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/qtf_webhook_alert_views_free.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'conflicts': ['qtf_omni_webhook_connector_pro'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'pre_init_hook': 'pre_init_check',
}
