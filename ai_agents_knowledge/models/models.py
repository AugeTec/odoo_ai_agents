# -*- coding: utf-8 -*-
from markdown.extensions.toc import slugify

from odoo import models, fields, api


class AI(models.Model):
    _inherit = 'ai_agents.ai'

    knowledge_article_ids = fields.Many2many('knowledge.article', string='Knowledge Articles')


class Task(models.Model):
    _inherit = 'ai_agents.task'

    def _list_data_points(self, request_context):
        """
        List the data points from the knowledge model

        :param request_context:
        :return:
        """

        res = super(Task, self)._list_data_points(request_context)
        article_titles = self.ai_id.knowledge_article_ids.mapped('name')
        article_titles = [slugify(title, "-") for title in article_titles]
        data_points = [f"knowledge_article_{article}" for article in article_titles]
        res.extend(data_points)
        return res

    def _retrieve_data(self, request_context, required_data_points):
        """
        Retrieve the data from the knowledge model
        :param request_context:
        :param required_data_points:
        :return:
        """

        res = super(Task, self)._retrieve_data(request_context, required_data_points)
        articles = self.ai_id.knowledge_article_ids
        for article in articles:
            title = article.name
            title_slug = slugify(f"knowledge_article_{title}", "-")
            if title_slug in required_data_points:
                # Markup to html
                article_body = article.body
                res[f"knowledge_article_{title}"] = article.body

        return res
