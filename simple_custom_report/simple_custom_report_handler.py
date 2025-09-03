from odoo import models
from odoo.tools import SQL


class SimpleCustomReportHandler(models.Model):
    _name = 'simple.custom.report.handler'
    _inherit = ['account.report.custom.handler']
    _description = "Handler for custom report"

    def _get_custom_groupby_map(self):
        def partner_label_builder(ids):
            res = {dic['id']: dic['name'] for dic in self.env['res.partner'].browse(id for id in ids if id).read(['name'])}
            res = dict(sorted(res.items(), key=lambda x:x[1]))
            if None in ids:
                res[None]: self.env._("Unknown")
            return res

        return {
            'partner_id': {
                'model': 'res.partner',
                'label_builder': partner_label_builder,
                'domain_builder': lambda grouping_key: [('partner_id', '=', grouping_key)]
            }
        }

    def _report_custom_engine_simple_custom_report(self, expressions, options, date_scope, current_groupby, next_groupby, offset=0, limit=None, warnings=None):
        subformulas = expressions.mapped('subformula')

        line_dicts = self._get_lines(subformulas, options, date_scope, current_groupby, offset, limit)

        if not current_groupby:
            return line_dicts[0] if line_dicts else {subformula: None for subformula in subformulas}

        return [(line_dict[current_groupby], line_dict | {'has_sublines': True})  for line_dict in line_dicts]

    def _get_select_clause(self, subformulas, query):
        select_clause = []

        for field_name in subformulas:
            field_expr = self.env['account.move.line']._field_to_sql('account_move_line', field_name, query)
            field = self.env['account.move.line']._fields[field_name]
            if field.type in ('integer', 'float', 'monetary'):
                field_expr = SQL('SUM(%s)', field_expr)
            else:
                field_expr = SQL('MAX(%s)', field_expr)

            select_clause.append(SQL('%s AS %s', field_expr, SQL.identifier(field_name)))

        return select_clause

    def _get_lines(self, subformulas, options, date_scope, groupby, offset=0, limit=None):
        report = self.env['account.report'].browse(options['report_id'])
        query = report._get_report_query(options, date_scope)
        query.add_where(SQL("account_move_line.debit > 0"))

        if groupby:
            query.groupby = self.env['account.move.line']._field_to_sql('account_move_line', groupby, query)
        if offset:
            query.offset = offset
        if limit:
            query.limit = limit

        select_clause = self._get_select_clause(subformulas, query)
        if groupby:
            select_clause.append(SQL('%s AS %s', query.groupby, SQL.identifier(groupby)))

        self.env.cr.execute(query.select(*select_clause))
        return self.env.cr.dictfetchall()
