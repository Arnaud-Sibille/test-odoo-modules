from odoo import fields, models


class TestModel(models.Model):
    _name = 'test.model'
    _description = "Test Model"

    name = fields.Char()

    date = fields.Date()

    today = fields.Date(default=fields.Date.today())

    context_today = fields.Date(
        compute="_compute_context_today",
        store=True,
        readonly=False,
    )

    def _compute_context_today(self):
        for test_model in self:
            test_model.context_today = fields.Date.context_today(test_model)
