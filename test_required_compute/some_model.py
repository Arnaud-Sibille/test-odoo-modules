from odoo import api, fields, models


class TestRequiredComputeSomeModel(models.Model):
    _name = 'test.required.compute.some.model'
    _description = "Some Model"

    required_field = fields.Char(required=True, default="Some value")

    required_field_length = fields.Integer(compute="_compute_required_field_length")

    @api.depends('required_field')
    def _compute_required_field_length(self):
        for some_model in self:
            some_model.required_field_length = len(some_model.required_field)
