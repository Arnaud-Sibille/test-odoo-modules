from odoo import fields, models

class SomeModel(models.Model):
    _name = 'some.model'
    _inherit = ['mail.thread']
    _description = "This is a description"

    name = fields.Char(tracking=True)
    amount = fields.Integer(tracking=True)
