from odoo import api, fields, models


class AModel(models.Model):
    _name = 'a.model'
    _description = "A Model"

    name = fields.Char()
    fixed_precision = fields.Float(digits=(15, 6))
    zero_precision = fields.Float(digits=0)
    no_precision = fields.Float()

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
