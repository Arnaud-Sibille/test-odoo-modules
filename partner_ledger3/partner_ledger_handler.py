from odoo import models


class PartnerLedgerHandler(models.AbstractModel):
    _name = 'partner.ledger.handler'
    _inherit = ['account.report.custom.handler']
    _description = "Handler for Partner Ledger"

    def _get_supported_expression_subformulas(self):
        return {
            'journal_id': {'expr': 'journal_id'},
            'account_code': {'expr': 'account_code'},
            'invoice_date': {'expr': 'invoice_date'},
            'date': {'expr': 'date'},
            'matching_number': {'expr': 'matching_number'},
            'debit': {'expr': 'debit'},
            'credit': {'expr': 'credit'},
            'amount_currency': {
                'expr': 'amount_currency',
                'convert_monetary': False,
            },
            'balance': {
                'expr': 'balance',
                'agg': 'cumulated_balance',
            },
        }

    def _report_custom_engine_partner_ledger_report(self, expressions, options, date_scope, current_groupby, next_groupby, offset=0, limit=None, warnings=None):
        if not current_groupby:
            return {expression.subformula: None for expression in expressions}

        if current_groupby == 'id':
            return self._get_move_lines(expressions, options)

        return self._get_grouped_lines(expressions, options, date_scope, current_groupby)

    def _get_move_lines(self, expressions, options):
        return []

    def _get_grouped_lines(self, expressions, options, date_scope, groupby):
        report = self.env['account.report'].browse(options['report_id'])
        query = report._get_report_query(options, date_scope)

        return []
