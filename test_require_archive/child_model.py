from odoo import fields, models


class ChildModel(models.Model):
    _name = 'child.model'
    _description = "Child Model"

    name = fields.Char()
    parent_model_id = fields.Many2one('parent.model')
