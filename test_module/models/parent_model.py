import random

from odoo import api, fields, models

class ParentModel(models.Model):
    _name = 'parent.model'
    _description = "Parent Model"

    name = fields.Char()

    total = fields.Float()

    monetary_amount = fields.Monetary(
        currency_field='non_stored_currency_id',
        compute="_compute_monetary_amount",
        store=True,
        readonly=False,
        copy=False,
    )

    non_stored_currency_id = fields.Many2one(
        'res.currency',
        compute="_compute_non_stored_currency_id",
    )

    non_stored_computed = fields.Float(
        compute="_compute_non_stored_computed",
    )

    @api.depends('name')
    def _compute_monetary_amount(self):
        for parent_model in self:
            parent_model.monetary_amount = random.randint(1, 100)

    @api.depends('total')
    def _compute_non_stored_computed(self):
        for parent_model in self:
            parent_model.non_stored_computed = parent_model.total * 2
    
    def _compute_non_stored_currency_id(self):
        for parent_model in self:
            random_index = random.randint(1, 100)
            parent_model.non_stored_currency_id = self.env['res.currency'].search([])[random_index]
