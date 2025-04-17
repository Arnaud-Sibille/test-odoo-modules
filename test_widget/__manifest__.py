{
    "name": "Test Widget",
    "description": "Testing widget",
    "author": "Arnaud S.",
    "license": "AGPL-3",
    "depends": ["base"],
    'data': [
        'views/views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'test_widget/static/src/**/*',
        ],
    },
}
