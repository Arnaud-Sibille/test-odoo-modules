{
    'name': "Test Mail Thread",
    'Description': "Some module to test mail.thread",
    'depends': ['mail'],
    'license': "AGPL-3",
    'author': 'Arnaud S.',
    'data': [
        'security/ir.model.access.csv',
        'views/some_model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'test_mail_thread/static/src/**/*',
        ]
    },
}