from odoo import api, fields, models

class ComputeToComputeModel(models.Model):
    _name = 'compute.to.compute.model'
    _description = "Test for compute dependancy recursion"

    an_amount = fields.Float(
        compute='_compute_an_amount',
        store=True,
        readonly=False,
    )
    inverse_of_that_amount = fields.Float(
        compute="_compute_inverse_of_that_amount",
        store=True,
        readonly=False,
    )


    @api.depends('inverse_of_that_amount')
    def _compute_an_amount(self):
        for record in self:
            if record.inverse_of_that_amount:
                record.an_amount = 1 / record.inverse_of_that_amount
            else:
                record.an_amount = 1

    @api.depends('an_amount')
    def _compute_inverse_of_that_amount(self):
        for record in self:
            if record.an_amount:
                record.inverse_of_that_amount = 1 / record.an_amount
            else:
                record.inverse_of_that_amount = 1
