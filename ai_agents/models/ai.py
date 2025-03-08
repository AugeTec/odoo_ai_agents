# -*- coding: utf-8 -*-
import json
import logging

import requests

from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AI(models.Model):
    _name = 'ai_agents.ai'
    _description = 'AI Connector'

    name = fields.Char()
    api_url = fields.Char()
    api_key = fields.Char()

    model_name = fields.Char()
    partner_id = fields.Many2one('res.partner', ondelete='cascade')

    base_context = fields.Text()

    # override create method to create a partner for the AI
    def create(self, vals):
        res = super(AI, self).create(vals)

        # Create a partner for the AI
        partner = self.env['res.partner'].create({
            'name': res.name + " AI",
            'email': f'__ai__{res.name}__'
        })

        res.partner_id = partner.id

        return res

    def generate(self, message):
        """
        Send a message to an ollama API
        """

        # Prepare the request
        headers = {
            'Content-Type': 'application/json',
        }

        data = {
            'model': self.model_name,
            'prompt': message,
        }

        response_text = ""

        # Send the request
        with requests.post(self.api_url + '/api/generate', headers=headers, data=json.dumps(data),
                           stream=True) as response:

            if response.status_code != 200:
                _logger.warning(f"AI response error: {response.text}")
                raise UserError(f"AI response error: {response.text}")

            # Read the response in chunks
            for line in response.iter_lines():
                try:
                    increment = json.loads(line)
                    response_text += increment['response']
                except json.JSONDecodeError:
                    pass

        return response_text

    def action_chat(self):
        """
        Start or find a conversation channel with the AI and post a message.
        """
        channel_model = self.env['discuss.channel']
        members = [self.partner_id.id, self.env.user.partner_id.id]
        uuid = f'{members[0]}-{members[1]}'
        # Check if a channel with this AI already exists
        channel = channel_model.search([('uuid', '=', uuid)], limit=1)

        # If not, create a new channel
        if not channel:
            channel = channel_model.create({
                'name': self.name,
                'channel_type': 'chat',
                'channel_partner_ids': [(4, partner_id) for partner_id in members],
                'uuid': uuid,
                'ai_id': self.id,
            })

        discuss_action = self.env.ref('mail.action_discuss').read()[0]
        # Open chat window
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web#action={discuss_action['id']}&active_id=discuss.channel_{channel.id}",

            'target': 'self',
        }
