# -*- coding: utf-8 -*-
# from odoo import http


# class AiAgentsKnowledge(http.Controller):
#     @http.route('/ai_agents_knowledge/ai_agents_knowledge', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ai_agents_knowledge/ai_agents_knowledge/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ai_agents_knowledge.listing', {
#             'root': '/ai_agents_knowledge/ai_agents_knowledge',
#             'objects': http.request.env['ai_agents_knowledge.ai_agents_knowledge'].search([]),
#         })

#     @http.route('/ai_agents_knowledge/ai_agents_knowledge/objects/<model("ai_agents_knowledge.ai_agents_knowledge"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ai_agents_knowledge.object', {
#             'object': obj
#         })

