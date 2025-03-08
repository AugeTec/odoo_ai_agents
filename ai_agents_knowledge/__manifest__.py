# -*- coding: utf-8 -*-
{
    'name': "AI Agents Knowledge",

    'summary': "Knowledge integration for AI Agents",

    'description': """
Use knowledge base articles in AI agents.
    """,

    'author': "Alexis Lopez Zubieta <alexis.lopez@augetec.com> (AUGE TEC)",
    'website': "https://augetec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'ai_agents', 'knowledge'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
