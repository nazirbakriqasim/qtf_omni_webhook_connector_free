# -*- coding: utf-8 -*-
from . import models
from odoo.exceptions import ValidationError

def pre_init_check(env):
    # Check if the PRO version is already installed
    pro_module = env['ir.module.module'].search([
        ('name', '=', 'qtf_omni_webhook_connector_pro'),
        ('state', '=', 'installed')
    ])
    if pro_module:
        raise ValidationError(
            "Installation Failed: The PRO version of this module is already installed on this system. "
            "Please uninstall the PRO version before installing the Free edition."
        )
