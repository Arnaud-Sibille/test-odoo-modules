from odoo import api, fields, models

class AModel(models.Model):
    _name = 'a.model'
    _description = "A Model"

    name = fields.Char()
    one_cron_id = fields.Many2one(
        comodel_name="ir.cron",
    )
    another_cron_id = fields.Many2one(
        comodel_name="ir.cron",
    )
    both_cron_ids = fiels.Many2many(
        comodel_name="ir.cron",
        compute="_compute_both_cron_ids",
    )

    @api.depends('one_cron_id', 'another_cron_id')
    def _compute_both_cron_ids(self):
        for record in self:
            record.both_cron_ids = one_cron_id | another_cron_id
