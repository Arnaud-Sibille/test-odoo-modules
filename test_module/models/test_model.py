from odoo import api, fields, models

class TestModel(models.Model):
    _name = 'test.model'
    _description = "Test Model"

    name = fields.Char()
