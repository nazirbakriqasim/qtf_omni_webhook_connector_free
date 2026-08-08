# -*- coding: utf-8 -*-
from odoo import models, api


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        """ Inherit creation layer routing alerts intelligently to group channel members or direct recipients """
        records = super(MailMessage, self).create(vals_list)
        for record in records:
            # Operational check: Ensure the message has text body and an author
            if record.body and record.author_id:

                # Dynamic Set to hold final targeted partner IDs to prevent duplicate alerts
                target_partner_ids = set()

                # Case 1: Direct Messages or Mentions via @ layout
                if record.partner_ids:
                    for partner in record.partner_ids:
                        target_partner_ids.add(partner.id)

                # Case 2: Standard Messages inside a Discuss Channel (Group Chat)
                if record.model == 'discuss.channel' and record.res_id:
                    channel = self.env['discuss.channel'].browse(record.res_id)
                    if channel and channel.channel_partner_ids:
                        for channel_partner in channel.channel_partner_ids:
                            target_partner_ids.add(channel_partner.id)

                # Process delivery if target partners are detected
                if target_partner_ids:
                    for partner_id in target_partner_ids:
                        partner = self.env['res.partner'].browse(partner_id)

                        # Match partner with active logged-in Odoo Users
                        if partner and partner.user_ids:
                            target_user = partner.user_ids[0]

                            # Fetch active gateway configuration record matching this specific recipient ID
                            provider = self.env['qtf.webhook.provider'].search([
                                ('qtf_active_provider', '=', True),
                                ('qtf_user_id', '=', target_user.id)
                            ], limit=1)

                            # Security Gate: Deliver only if provider is active AND recipient is NOT the author
                            if provider and record.create_uid.id != target_user.id:

                                raw_text = record.body or ""
                                # Normalize and safely strip HTML tags from the data string
                                clean_text = raw_text.replace('<p>', '').replace('</p>', '\n').replace('<br>',
                                                                                                       '\n').replace(
                                    '<br/>', '\n')

                                while "<" in clean_text and ">" in clean_text:
                                    start = clean_text.find("<")
                                    end = clean_text.find(">") + 1
                                    clean_text = clean_text[:start] + clean_text[end:]

                                # Format final messaging output context layout
                                final_msg = f"تنبيه رسالة جديدة 🔔\nالمصدر: #{record.record_name or 'محادثة'}\nالمرسل: {record.author_id.name}\n\nالمحتوى:\n{clean_text.strip()}"

                                # Fire outbound network dispatch to the user's registered terminal mapping
                                provider.qtf_send_dynamic_alert(provider.qtf_recipient_chat_id, final_msg)
        return records
