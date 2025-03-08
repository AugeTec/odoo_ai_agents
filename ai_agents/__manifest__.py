# -*- coding: utf-8 -*-
{
    'name': "AI Agents",

    'summary': "AI Agents for Odoo",

    'description': """
    AI Agents for Odoo
    
    This module provides a framework for using AI agents in Odoo to automate tasks and provide assistance to users.
    """,

    'author': "Alexis Lopez Zubieta <alexis.lopez@augetec.com> (AUGE TEC)",
    'website': "https://augtec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'web'],
    'assets': {
        'web.assets_backend': [
            ('append', 'ai_agents/static/src/core/common/thread_service.js'),
        ],
        # For frontend assets, if needed:
        # 'web.assets_frontend': [
        #     ('append', 'path/to/your/frontend/file.js'),
        # ],
    },
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/ai.xml',
        'views/task.xml',
        'views/templates.xml',
        # Data
        'data/cronjobs.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    "application": True,
}
