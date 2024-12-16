{
    "name": "Test module",
    "description": "For testing purpose",
    "author": "Arnaud S.",
    "license": "AGPL-3",
    "depends": ["base"],
    'data': [
        'security/ir.model.access.csv',
        'views/test_model_views.xml',
        'views/parent_model_views.xml',
        'views/menuitems.xml',
    ],
    'post_init_hook': 'post_init_hook',
}
