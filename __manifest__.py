# -*- coding: utf-8 -*-
{
    'name': "travels_erp",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence_data.xml',
        'views/views.xml',
        'views/templates.xml',
        'reports/invoice_template.xml',
        'reports/invoice_report.xml',
            'views/states.xml',
        'views/cities.xml',
        'views/countries.xml',
        'views/form_itinerary.xml',
        'views/hotels.xml',
        'views/expense.xml',
        'views/invoices.xml',
        'views/road_transport.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
       'installable': True,
    'application': True,
       'assets': {
   'web.assets_backend': [
    
       '/travels_erp/static/src/js/dashboard/dashboard.js',
       '/travels_erp/static/src/xml/dashboard/dashboard.xml',
       '/travels_erp/static/src/js/itinerary/itinerary.js',
       '/travels_erp/static/src/js/itinerary/edit_itinerary.js',
       '/travels_erp/static/src/xml/itinerary/itinerary.xml',
       '/travels_erp/static/src/xml/itinerary/edit_itinerary.xml',
       '/travels_erp/static/src/xml/**/*.xml',
       '/travels_erp/static/src/js/**/*.xml',
       

       '/travels_erp/static/src/css/*.css',
       '/travels_erp/static/src/components/table/datagrid.xml',
       '/travels_erp/static/src/components/table/datagrid.js',
       '/travels_erp/static/src/components/autocomplete/autocomplete.xml',
       '/travels_erp/static/src/components/autocomplete/autocomplete.js',
   ],
},
}


