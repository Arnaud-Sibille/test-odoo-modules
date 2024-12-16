from . import models

def post_init_hook(env):
    env['res.currency'].with_context(active_test=False).search([]).write({'active': True})
