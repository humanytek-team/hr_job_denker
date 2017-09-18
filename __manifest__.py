# -*- coding: utf-8 -*-
{
    'name' : 'Perfil de puesto Denker',
    'version' : '1',
    'author': 'Humanytek',
    'description': """
    
    """,
    'category' : 'Employees',
    'depends' : ['hr','hr_recruitment'],
    'data': [
        'hr_job_view.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'report/perfil_puesto_format.xml',
        
    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
