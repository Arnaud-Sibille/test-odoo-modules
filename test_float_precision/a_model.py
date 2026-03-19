from odoo import api, fields, models


class AModel(models.Model):
    _name = 'a.model'
    _description = "A Model"

    name = fields.Char()
    fixed_precision = fields.Float(digits=(15, 6))
    zero_precision = fields.Float(digits=0)
    no_precision = fields.Float()
    price_unit = fields.Float(min_display_digits="Product Price")
    currency_id = fields.Many2one('res.currency')
    price = fields.Monetary()

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
