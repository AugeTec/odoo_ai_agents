from datetime import datetime

import markdown
import requests
from markupsafe import Markup

from odoo import models, fields, api
from odoo.tools.safe_eval import json


class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    ai_id = fields.Many2one('ai_agents.ai')
    ai_tasks = fields.One2many('ai_agents.task', 'channel_id')

    def message_post(self, **kwargs):
        res = super(DiscussChannel, self).message_post(**kwargs)

        if self.ai_id and res.author_id != self.ai_id.partner_id:
            task = self.ai_tasks.create({
                'user_input': self.message_ids[0].body,
                'channel_id': self.id,
                'user_id': self.env.user.id,
                'user_context': json.dumps(self.env.context),
            })

            # notify user typing
            member = self._find_or_create_member_for_ai()
            member._notify_typing(True)

            # trigger the task
            # self._cron_process_ai_tasks()

        return res

    def _find_or_create_member_for_ai(self):
        self.ensure_one()
        domain = [("channel_id", "=", self.id), ("partner_id", "in", self.ai_id.partner_id.ids)]
        member = self.env["discuss.channel.member"].search(domain)
        if member:
            return member

        return self.add_members(partner_ids=self.ai_id.partner_id.ids)


