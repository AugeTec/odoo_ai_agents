# -*- coding: utf-8 -*-

from odoo import http


class MiaRunnerController(http.Controller):
    @http.route('/mia/task/execute', auth='public', methods=['POST'], csrf=False)
    def runner(self, **kw):
        # Call the cronjob to process the AI tasks
        http.request.env['discuss.channel'].sudo()._cron_process_ai_tasks()
        return "OK"
