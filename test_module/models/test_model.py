import random

from odoo import api, fields, models

class TestModel(models.Model):
    _name = 'test.model'
    _description = "Test Model"

    name = fields.Char()

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required=True,
    )
    amount = fields.Monetary(
        currency_field='currency_id',
        compute="_compute_amount",
        store=True,
        readonly=False,
        copy=False,
    )
    amount_times_5 = fields.Float(
        compute='_compute_amount_times_5',
    )

    parent_model_id = fields.Many2one(
        'parent.model',
    )
    parent_model_total = fields.Float(
        related='parent_model_id.total',
    )
    parent_model_non_stored_computed = fields.Float(
        related='parent_model_id.non_stored_computed',
    )

    @api.depends('name')
    def _compute_amount(self):
        for test_model in self:
            test_model.amount = random.randint(1, 100)

    @api.depends('amount')
    def _compute_amount_times_5(self):
        for test_model in self:
            test_model.amount_times_5 = 5 * test_model.amount
