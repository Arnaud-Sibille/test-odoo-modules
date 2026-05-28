from odoo import api, fields, models

class SomeModel(models.Model):
    _name = 'some.model'
    _description = "Some Model"

    name = fields.Char()
    active = fields.Boolean(default=True)
    something = fields.Char()

    @api.model
    def get_empty_list_help(self, help_message: str) -> str:
        return "<div>yo</div>"

