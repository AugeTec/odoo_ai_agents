import logging

import markdown
from markupsafe import Markup

from odoo import models, api, fields, _
from odoo.addons.test_convert.tests.test_env import field
from odoo.tools.safe_eval import json

_logger = logging.getLogger(__name__)


class Task(models.Model):
    _name = 'ai_agents.task'
    _description = 'AI Task'

    name = fields.Char(default='Agent Task')
    ai_id = fields.Many2one('ai_agents.ai', related='channel_id.ai_id')

    channel_id = fields.Many2one('discuss.channel', ondelete='cascade')

    user_input = fields.Text()
    user_id = fields.Many2one('res.users')
    user_context = fields.Text()
    prompt = fields.Text()

    response = fields.Text()
    error_message = fields.Text()
    status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('error', 'Error')
    ], default='pending')

    def generate_response(self):
        self.ensure_one()
        request_context = self._load_request_context()
        context_data = self._retrieve_context_data(request_context)
        self._prepare_response(context_data)

    def _retrieve_context_data(self, request_context):
        context_data = {}

        available_data_points = self._list_data_points(request_context)
        required_data_points = []

        if available_data_points:
            required_data_points = self._asses_required_data_points(available_data_points)

        if required_data_points:
            context_data = self._retrieve_data(request_context, required_data_points)

        return context_data

    def _prepare_response(self, context_data):
        chat_context = ''
        try:
            chat_context += 'Mensaje:\n'
            chat_context += self.user_input + '\n\n'

            chat_context = f'Context: {self.ai_id.base_context}\n\n'
            chat_context += f'Data:\n```json\n{json.dumps(context_data)}```\n\n'

            # get conversation
            # chat_context += self._get_message_history()

            # send the message to the AI
            response = self.ai_id.generate(chat_context)

            # format response from markdown to html
            html_response = markdown.markdown(response)
            markup = Markup(html_response)

            # create a new message with the response
            self.channel_id.sudo().message_post(
                body=markup, author_id=self.ai_id.partner_id.id,
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

            self.sudo().write({
                'prompt': chat_context,
                'response': response,
                'status': 'completed'
            })
        except Exception as e:
            self.sudo().write({
                'prompt': chat_context,
                'error_message': str(e),
                'status': 'error'
            })

            # notify error
            error_message = Markup(f'There was an error while generating the response.')
            self.channel_id.message_post(
                body=error_message, author_id=self.ai_id.partner_id.id,
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

    def _asses_required_data_points(self, available_data_points):
        """ Asses the need for additional information.
        - check if we need knowledge about the context
        """
        self.ensure_one()

        # check if we need knowledge about the context in order to generate a better response based on the user input

        instruction = "Asses if we need some of the following data points in order to generate a better response to the user input.\n"
        instruction += "User input:\n" + self.user_input + "\n\n"
        instruction += f"Available data points:\n```json{json.dumps(available_data_points)}```\n\n"

        instruction += "Your response must only be json array with required data field names.\n"
        instruction += "Example output: ```json\n['model', 'id', 'action', 'menu_id', 'view_type']```\n"

        try:
            response = self.ai_id.generate(instruction)
            response = response.strip()

            # extract json block from the response which is contained between ```json and ``` characters
            json_block_idx = response.find('```json')
            if json_block_idx != -1:
                json_block_end_idx = response.find('```', json_block_idx + 6)
                response = response[json_block_idx + 7:json_block_end_idx]

            response = json.loads(response)
            return response
        except Exception as e:
            _logger.warning(f"Error while analysing request: {e}")
            return {}

    def _load_request_context(self):
        """ Load context from the user context field """
        user_context = json.loads(self.user_context)
        frontend_context = user_context.get('frontend', {})

        model = None
        if "model" in frontend_context:
            model = self.env[frontend_context['model']]

        record = None
        if "id" in frontend_context and model is not None:
            record_id = frontend_context['id']
            record_id = int(record_id) if record_id.isdecimal() else record_id
            record = model.browse([record_id])

        action = None
        if "action" in frontend_context:
            # get action from frontend context
            action_id = frontend_context['action']
            action_id = int(action_id) if action_id.isdecimal() else action_id

            action = self.env['ir.actions.actions'].browse([action_id])

        menu = None
        if "menu_id" in frontend_context:
            menu_id = frontend_context['menu_id']
            menu_id = int(menu_id) if menu_id.isdecimal() else menu_id
            menu = self.env['ir.ui.menu'].browse([menu_id])

        view_type = None
        if "view_type" in frontend_context:
            view_type = frontend_context['view_type']

        request_context = {
            'model': model,
            'record': record,
            'action': action,
            'menu': menu,
            'view_type': view_type,
            'user': self.user_id,
        }

        return request_context

    def _get_frontend_context(self):
        user_context = json.loads(self.user_context)
        frontend_context = user_context.get('frontend', {})
        frontend_context_readable = {}

        model = None
        if "model" in frontend_context:
            model = self.env[frontend_context['model']]
            frontend_context_readable['model'] = model.display_name

        if "id" in frontend_context and model is not None:
            record_id = frontend_context['id']
            record_id = int(record_id) if record_id.isdecimal() else record_id
            record = model.browse([record_id])
            frontend_context_readable['record'] = record.display_name

        if "action" in frontend_context:
            # get action from frontend context
            action_id = frontend_context['action']
            action_id = int(action_id) if action_id.isdecimal() else action_id

            action = self.env['ir.actions.actions'].browse([action_id])
            if action:
                frontend_context_readable['action'] = action.display_name

        if "menu_id" in frontend_context:
            menu_id = frontend_context['menu_id']
            menu_id = int(menu_id) if menu_id.isdecimal() else menu_id
            menu = self.env['ir.ui.menu'].browse([menu_id])
            if menu:
                frontend_context_readable['menu'] = menu.display_name

        if "view_type" in frontend_context:
            frontend_context_readable['view_type'] = frontend_context['view_type']

        extended_context = {'user': self.env.user.display_name, 'frontend': frontend_context_readable}
        chat_context = f"Context:```{json.dumps(extended_context)}```\n\n"

        if "model" in frontend_context and "view_type" in frontend_context:
            # get views
            view_type = frontend_context['view_type']
            view_res = model.get_views([(None, view_type)])
            # domains
            data_domains = {}
            if "model" in frontend_context and 'id' in frontend_context:
                data_domains[frontend_context["model"]] = [('id', '=', frontend_context['id'])]

            for model_name, data in view_res['models'].items():
                data_domains[model_name] = []
                for fild_name, field_data in data.items():
                    if "relation" in field_data:
                        related_model = field_data["relation"]
                        if related_model:
                            if related_model not in data_domains:
                                data_domains[related_model] = []

                            data_domains[related_model].append((fild_name, 'in', [record.id]))
                            data_domains[related_model].extend(field_data["domain"])

            # gather data from models
            chat_context += 'Data on display:\n\n'
            for model_name, data in view_res['models'].items():
                specification = {k: {} for k, _ in data.items()}
                domain = data_domains.get(model_name, [])

                target_model = self.env[model_name].with_context(**user_context)
                model_data = target_model.web_search_read(domain=domain, specification=specification)
                data_csv = self._generate_data_csv(model_data)

                chat_context += (f"{model_name}: ```csv\n{data_csv}```\n")

        return chat_context

    def _generate_data_csv(self, model_data):
        data_csv = ''
        if model_data['length'] == 0:
            return data_csv

        keys = model_data['records'][0].keys()
        data_csv += ','.join(keys) + '\n'
        for record in model_data['records']:
            data_csv += ','.join([str(record[key]) for key in keys]) + '\n'

        return data_csv

    def _get_message_history(self, limit=4):
        selected_messages = self.channel_id.message_ids[:limit - 1]
        chat_context = 'Previous Messages:\n\n'
        for message in reversed(selected_messages):
            chat_context += message.body + '\n\n'

        return chat_context

    @api.model
    def _cron_process_ai_tasks(self):
        tasks = self.env['ai_agents.task'].search([('status', '=', 'pending')])
        for task in tasks:
            task.generate_response()
            member = task.channel_id._find_or_create_member_for_ai()

            # stop typing
            member._notify_typing(False)
            task.status = 'completed'

    def _list_data_points(self, request_context):
        """ List available data points for the request context """
        return []

    def _retrieve_data(self, request_context, required_data_points):
        retrieved_data = {}

        return retrieved_data
