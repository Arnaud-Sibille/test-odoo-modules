from odoo import api, fields, models


class InverseToInverseModel(models.Model):
    _name = 'inverse.to.inverse.model'
    _description = "Inverse To Inverse Model"

    an_amount = fields.Float(
        inverse="_inverse_an_amount",
        digits=0,
    )
    inverse_of_that_amount = fields.Float(
        inverse="_inverse_inverse_of_that_amount",
        digits=0,
    )


    @api.onchange('an_amount')
    def _inverse_an_amount(self):
        for record in self:
            if record.an_amount:
                record.inverse_of_that_amount = 1 / record.an_amount
            else:
                record.inverse_of_that_amount = 1

    @api.onchange('inverse_of_that_amount')
    def _inverse_inverse_of_that_amount(self):
        for record in self:
            if record.inverse_of_that_amount:
                record.an_amount = 1 / record.inverse_of_that_amount
            else:
                record.an_amount = 1
