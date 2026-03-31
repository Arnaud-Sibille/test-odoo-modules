from odoo import fields, models


class ParentModel(models.Model):
    _name = 'parent.model'
    _description = "Parent Model"

    name = fields.Char()
    active = fields.Boolean(default=True)
