from odoo import api, fields, models
from odoo.tools import str2bool, SQL


MODEL = 'account.move.line'
ALIAS = 'account_move_line'
ORDER_CLAUSE = SQL('%(alias)s.date, %(alias)s.move_name, %(alias)s.id', alias=SQL(ALIAS))
CURRENCY_TABLE_ALIAS = 'currency_rates'
CURRENCY_TABLE_JOIN_CONDITION = f'%(currency_field_expr)s = {CURRENCY_TABLE_ALIAS}.currency_id AND EXTRACT(YEAR FROM %(date_field_expr)s) = {CURRENCY_TABLE_ALIAS}.year'


class PartnerLedger2ReportHandler(models.AbstractModel):
    _name = 'partner.ledger2.report.handler'
    _inherit = ['account.report.custom.handler']
    _description = "Partner Ledger 2 Custom Handler"


    ####################################################
    # Report Framework
    ####################################################

    def _get_custom_display_config(self):
        return {
            'css_custom_class': 'partner_ledger',
            'components': {
                'AccountReportLineCell': 'account_reports.PartnerLedgerLineCell',
            },
            'templates': {
                'AccountReportLineName': 'account_reports.PartnerLedgerLineName',
            },
        }

    def _get_custom_groupby_map(self):
        return {
            'id': {
                'model': None,
                'label_builder': self._partner_ledger_move_line_label_builder,
                'sorted': True,
            },
        }

    def _partner_ledger_move_line_label_builder(self, key):
        if not key:
            return 'Initial Values'
        return self.env['account.move.line'].browse(key).display_name

    ####################################################
    # Core
    ####################################################

    def _report_custom_engine_partner_ledger_report(self, expressions, options, date_scope, current_groupby, next_groupby, offset=0, limit=None, warnings=None):
        none_dict = {expression.subformula: None for expression in expressions}

        if not current_groupby:
            return none_dict

        if current_groupby == 'id':
            prev_groupbys = expressions.report_line_id.groupby.split(',')[:-1]
            line_dicts = self._get_move_lines(self._parse_expressions(expressions), prev_groupbys, options)

        else:
            line_dicts = self._get_grouped_lines(self._parse_expressions(expressions), [current_groupby], options)

        return [(line_dict[current_groupby], none_dict | line_dict) for line_dict in line_dicts]

    def _parse_expressions(self, expressions):
        parsed_expressions = []

        for expression in expressions:
            field, agg, paramaters_dict = self._parse_subformula(expression.subformula)
            parsed_expressions.append({
                'subformula': expression.subformula,
                'field': field,
                'agg': agg,
                'parameters_dict': paramaters_dict,
            })

        return parsed_expressions

    @api.model
    def _parse_subformula(self, subformula):
        field, *rest_of_subformula = subformula.split(':')
        if not rest_of_subformula:
            return field, False, {}

        agg, parameters = rest_of_subformula
        if not parameters:
            return field, agg, {}

        parameters_dict = {}
        for key_value_str in parameters.split(','):
            key, value = key_value_str.split('=')
            try:
                parameters_dict[key] = str2bool(value)
            except ValueError:
                parameters_dict[key] = value

        return field, agg, parameters_dict

    def _get_grouped_lines(self, expression_dicts, groupbys, options):
        strict_range_sql = self._get_grouped_lines_sql(
            [expression_dict for expression_dict in expression_dicts if expression_dict['agg'] != 'cumulated_sum'],
            groupbys, options, 'strict_range',
        )
        full_range_sql = self._get_grouped_lines_sql(
            [expression_dict for expression_dict in expression_dicts if expression_dict['agg'] == 'cumulated_sum'],
            groupbys, options, 'from_beginning',
        )

        final_sql = SQL('')
        if strict_range_sql and full_range_sql:
            strict_range_alias = SQL('strict_range_table')
            full_range_alias = SQL('full_range_table')

            final_selects = []
            full_join_conditions = []

            for groupby in groupbys:
                final_selects.append(SQL(
                    'COALESCE(%(strict_range_alias)s.%(groupby)s, %(full_range_alias)s.%(groupby)s) AS "%(groupby)s"',
                    strict_range_alias=strict_range_alias,
                    full_range_alias=full_range_alias,
                    groupby=SQL(groupby)
                ))
                full_join_conditions.append(SQL(
                    '%(strict_range_alias)s."%(groupby)s"=%(full_range_alias)s."%(groupby)s"',
                    strict_range_alias=strict_range_alias,
                    full_range_alias=full_range_alias,
                    groupby=SQL(groupby),
                ))

            final_selects += [SQL(
                '%(table)s."%(subformula)s" AS "%(subformula)s"',
                table=strict_range_alias if expression_dict['agg'] != 'cumulated_sum' else full_range_alias,
                subformula=SQL(expression_dict['subformula'])
            ) for expression_dict in expression_dicts]

            final_sql = SQL('''
                    WITH
                        %(currency_table_alias)s AS (%(currency_table_sql)s),
                        %(strict_range_alias)s AS (%(strict_range_sql)s),
                        %(full_range_alias)s AS (%(full_range_sql)s)
                    SELECT
                        %(final_select_clause)s
                    FROM
                        %(strict_range_alias)s
                    FULL JOIN
                        %(full_range_alias)s ON %(full_join_condition)s
                ''',
                currency_table_alias=SQL(CURRENCY_TABLE_ALIAS),
                currency_table_sql=self._get_currency_table(),
                strict_range_alias=strict_range_alias,
                strict_range_sql=strict_range_sql,
                full_range_alias=full_range_alias,
                full_range_sql=full_range_sql,
                final_select_clause=SQL(', ').join(final_selects),
                full_join_condition=SQL(' AND ').join(full_join_conditions),
            )
        elif strict_range_sql:
            final_sql = SQL(
                'WITH %(currency_table_alias)s AS (%(currency_table_sql)s) %(strict_range_sql)s',
                currency_table_alias=SQL(CURRENCY_TABLE_ALIAS),
                currency_table_sql=self._get_currency_table(),
                strict_range_sql=strict_range_sql,
            )

        print(self._cr._format(final_sql))
        self._cr.execute(final_sql)
        return self._cr.dictfetchall()

    def _get_grouped_lines_sql(self, expression_dicts, groupbys, options, date_scope):
        if not expression_dicts:
            return False

        report = self.env['account.report'].browse(options['report_id'])
        query = report._get_report_query(options, date_scope)

        select_clause = [
            SQL('%s AS "%s"', self._get_select_expr(query, groupby, agg='groupby'), SQL(groupby))
        for groupby in groupbys]
        for expression_dict in expression_dicts:
            expr = SQL('NULL')
            if agg := expression_dict['agg']:
                expr = self._get_select_expr(
                    query,
                    expression_dict['field'],
                    agg=agg,
                    cumulated_sum=False, # only used for non grouped move lines
                    conv_mon=expression_dict['parameters_dict'].get('conv_mon'),
                    mon_date_field=expression_dict['parameters_dict'].get('mon_date_field'),
                )
            select_clause.append(SQL('%s AS "%s"', expr, SQL(expression_dict['subformula'])))

        return query.select(*select_clause)

    def _get_select_expr(self, query, field_path, agg=False, cumulated_sum=False, partition_expr=False, conv_mon=False, mon_date_field=False):
        field_expr, field_name, field_model, field_table_alias = self._field_path_to_sql(field_path, self.env[MODEL], ALIAS, query)

        field = field_model._fields[field_name]
        if field.type == 'monetary' and conv_mon:
            field_expr = self._get_currency_converted_expr(field_expr, query, field, field_model, field_table_alias, mon_date_field)

        if agg in ('sum', 'cumulated_sum'):
            field_expr = SQL('SUM(%s)', field_expr)

        # cumulated sum is when we don't aggregate (so no groupby) 
        elif not agg and cumulated_sum:
            field_expr = SQL('SUM(%s) OVER (PARTITION BY (%s) ORDER BY %s)', field_expr, partition_expr, ORDER_CLAUSE)

        elif agg == 'groupby':
            self._add_groupby(field_expr, query)

        return field_expr

    def _field_path_to_sql(self, field_path, current_model, current_alias, query):
        field_names = field_path.split('.')

        for field_name in field_names[:-1]:
            field = current_model._fields[field_name]

            comodel = self.env[field.comodel_name]
            coalias = query.left_join(
                current_alias,
                field_name,
                comodel._table,
                'id',
                field_name,
            )

            current_model, current_alias = comodel, coalias

        last_field_name = field_names[-1]

        return (
            current_model._field_to_sql(current_alias, last_field_name, query),
            last_field_name,
            current_model,
            current_alias,
        )

    def _get_currency_converted_expr(self, expr, query, field, model, field_table_alias, date_field_name):
        currency_field_name = field.get_currency_field(model)

        currency_field_expr = model._field_to_sql(field_table_alias, currency_field_name, query)
        date_field_expr, *_ = self._field_path_to_sql(date_field_name, self.env[MODEL], ALIAS, query)

        currency_table_alias = self._join_with_currency_table(currency_field_expr, date_field_expr, query)

        return SQL('%s / COALESCE(%s.rate, 1)', expr, SQL(CURRENCY_TABLE_ALIAS))

    def _join_with_currency_table(self, currency_field_expr, date_field_expr, query):
        cur_table_join_condition = SQL(
            CURRENCY_TABLE_JOIN_CONDITION,
            currency_field_expr=currency_field_expr,
            date_field_expr=date_field_expr,
        )
        query.add_join('left join', CURRENCY_TABLE_ALIAS, CURRENCY_TABLE_ALIAS, cur_table_join_condition)

    def _add_groupby(self, groupby, query):
        if not query.groupby:
            query.groupby = SQL(groupby)
        else:
            query.groupby = SQL('%s, %s', query.groupby, groupby)

    def _get_currency_table(self):
        return SQL("""
            SELECT DISTINCT ON (res_currency_rate.currency_id, EXTRACT(YEAR FROM res_currency_rate.name))
                res_currency_rate.currency_id,
                EXTRACT(YEAR FROM res_currency_rate.name) AS year,
                res_currency_rate.rate
            FROM res_currency_rate
            JOIN res_currency ON res_currency_rate.currency_id = res_currency.id
            WHERE
                res_currency.active IS TRUE
                AND res_currency_rate.company_id = %s
            ORDER BY
                res_currency_rate.currency_id,
                EXTRACT(YEAR FROM res_currency_rate.name),
                res_currency_rate.name DESC
        """, self.env.company.id)

    def _get_move_lines(self, expression_dicts, prev_groupbys, options):
        report = self.env['account.report'].browse(options['report_id'])

        strict_range_sql = self._get_move_lines_sql(
            expression_dicts,
            prev_groupbys,
            options,
            'strict_range',
        )
        date_from, _date_to = report._get_date_bounds_info(options, None)
        initial_values_options = options | {'date': report._get_dates_period(None, fields.Date.from_string(date_from), 'single')}
        initial_values_sql = self._get_grouped_lines_sql(
            [expression_dict for expression_dict in expression_dicts if expression_dict['agg'] == 'cumulated_sum'],
            prev_groupbys,
            initial_values_options,
            'from_beginning',
        )

        final_sql = SQL('')
        if strict_range_sql and initial_values_sql:
            strict_range_alias = SQL('strict_range_table')
            initial_values_alias = SQL('initial_values_table')

            final_selects = [SQL('%s.id AS id', strict_range_alias), SQL('%s.row_num AS row_num', strict_range_alias)]
            initial_values_selects = [SQL('NULL AS id'), SQL('0 AS row_num')]
            full_join_conditions = []
            for groupby in prev_groupbys:
                final_selects.append(SQL(
                    '%(strict_range_alias)s."%(groupby)s" AS "%(groupby)s"',
                    strict_range_alias=strict_range_alias,
                    groupby=SQL(groupby),
                ))
                initial_values_selects.append(SQL(
                    '%(initial_values_alias)s."%(groupby)s" AS "%(groupby)s"',
                    initial_values_alias=initial_values_alias,
                    groupby=SQL(groupby),
                ))
                full_join_conditions.append(SQL(
                    '%(strict_range_alias)s."%(groupby)s"=%(initial_values_alias)s."%(groupby)s"',
                    strict_range_alias=strict_range_alias,
                    initial_values_alias=initial_values_alias,
                    groupby=SQL(groupby),
                ))
            for expression_dict in expression_dicts:
                subformula = SQL(expression_dict['subformula'])
                final_select_field_expr = SQL('%s."%s"', strict_range_alias, subformula)
                initial_values_field_expr = SQL('NULL')
                if expression_dict['agg'] == 'cumulated_sum':
                    final_select_field_expr = SQL(
                        'COALESCE(%s, 0) + COALESCE(%s, 0)',
                        final_select_field_expr,
                        SQL('%s."%s"', initial_values_alias, subformula)
                    )
                    initial_values_field_expr = SQL('%s."%s"', initial_values_alias, subformula)

                final_selects.append(SQL('%s AS "%s"', final_select_field_expr, subformula))
                initial_values_selects.append(SQL('%s AS "%s"', initial_values_field_expr, subformula))

            final_sql = SQL('''
                    WITH
                        %(currency_table_alias)s AS (%(currency_table_sql)s),
                        %(strict_range_alias)s AS (%(strict_range_sql)s),
                        %(initial_values_alias)s AS (%(initial_values_sql)s)
                    SELECT %(initial_values_select_clause)s FROM %(initial_values_alias)s
                    UNION ALL
                    SELECT %(final_select_clause)s FROM %(strict_range_alias)s
                    LEFT JOIN %(initial_values_alias)s ON %(full_join_condition)s
                    ORDER BY %(order)s
                ''',
                currency_table_alias=SQL(CURRENCY_TABLE_ALIAS),
                currency_table_sql=self._get_currency_table(),
                strict_range_alias=strict_range_alias,
                strict_range_sql=strict_range_sql,
                initial_values_alias=initial_values_alias,
                initial_values_sql=initial_values_sql,
                initial_values_select_clause=SQL(', ').join(initial_values_selects),
                final_select_clause=SQL(', ').join(final_selects),
                full_join_condition=SQL(' AND ').join(full_join_conditions),
                order= SQL(', ').join([SQL('"%s"', SQL(groupby)) for groupby in prev_groupbys] + [SQL('row_num')]),
            )

        elif strict_range_sql:
            final_sql = SQL(
                'WITH %(currency_table_alias)s AS (%(currency_table_query)s) %(strict_range_sql)s',
                currency_table_alias=SQL(CURRENCY_TABLE_ALIAS),
                currency_table_query=self._get_currency_table(),
                strict_range_sql=strict_range_sql,
            )

        print(self._cr._format(final_sql))
        self._cr.execute(final_sql)
        return self._cr.dictfetchall()

    def _get_move_lines_sql(self, expression_dicts, prev_groupbys, options, date_scope):
        if not expression_dicts:
            return False

        report = self.env['account.report'].browse(options['report_id'])
        query = report._get_report_query(options, date_scope)

        select_clause = [
            SQL('%s AS "%s"', self._get_select_expr(query, groupby, agg=False), SQL(groupby))
        for groupby in prev_groupbys] + [
            SQL('%s.id AS id', SQL(ALIAS)),
            SQL('ROW_NUMBER() OVER (ORDER BY %s) AS row_num', ORDER_CLAUSE),
        ]

        partition_expr = SQL(', ').join(self._field_path_to_sql(groupby, self.env[MODEL], ALIAS, query)[0] for groupby in prev_groupbys)
        for expression_dict in expression_dicts:
            expr = self._get_select_expr(
                query,
                expression_dict['field'],
                agg=False,
                cumulated_sum=expression_dict['agg'] == 'cumulated_sum',
                partition_expr=partition_expr,
                conv_mon=expression_dict['parameters_dict'].get('conv_mon'),
                mon_date_field=expression_dict['parameters_dict'].get('mon_date_field'),
            )
            select_clause.append(SQL('%s AS "%s"', expr, SQL(expression_dict['subformula'])))

        return query.select(*select_clause)

    def _custom_unfold_all_batch_data_generator(self, report, options, lines_to_expand_by_function):
        def build_full_sub_groupby_key(report_line_id, full_sub_groupby_key_elements, current_groupby):
            return f"[{report_line_id}]{','.join(full_sub_groupby_key_elements)}=>{current_groupby}"

        def add_line_dict_to_rslt_dict(rslt, line_dict, column_group_key, key, groupby, expressions):
            rslt.setdefault(key, {}).setdefault(column_group_key, {})
            for expression in expressions:
                rslt[key][column_group_key].setdefault(expression, {}).setdefault('value', []).append((line_dict[groupby], line_dict.get(expression.subformula)))
                sublines_info = rslt[key][column_group_key].setdefault(expression, {}).setdefault('sublines_info', set())
                if groupby != 'id':
                    sublines_info.add(line_dict[groupby])

        rslt = {}

        for expand_function_name, lines_to_expand in lines_to_expand_by_function.items():
            for line_to_expand in lines_to_expand:
                if expand_function_name == '_report_expand_unfoldable_line_with_groupby':
                    report_line_id = report._get_res_id_from_line_id(line_to_expand['id'], 'account.report.line')
                    report_line = self.env['account.report.line'].browse(report_line_id)
                    expressions = report_line.expression_ids
                    for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
                        groupbys = report_line.groupby.split(',')
                        for i, groupby in enumerate(groupbys):
                            if groupby != 'id':
                                line_dicts = self._get_grouped_lines(self._parse_expressions(expressions), groupbys[:i + 1], column_group_options)
                            else:
                                line_dicts = self._get_move_lines(self._parse_expressions(expressions), groupbys[:i], column_group_options)
                            for line_dict in line_dicts:
                                key = build_full_sub_groupby_key(report_line_id, [f"{groupby_}:{line_dict[groupby_]}" for groupby_ in groupbys[:i]] , groupby)
                                add_line_dict_to_rslt_dict(rslt, line_dict, column_group_key, key, groupby, expressions)

        return rslt


    ####################################################
    # Misc
    ####################################################

    @api.model
    def action_open_record(self, options, params):
        model, record_id = self.env['account.report']._get_model_info_from_id(params['id'])
        return {
            'type': 'ir.actions.act_window',
            'res_model': model,
            'res_id': record_id,
            'views': [[False, 'form']],
            'view_mode': 'form',
            'target': 'current',
        }

    def open_journal_items(self, options, params):
        params['view_ref'] = 'account.view_move_line_tree_grouped_partner'
        report = self.env['account.report'].browse(options['report_id'])
        action = report.open_journal_items(options=options, params=params)
        action.get('context', {}).update({'search_default_group_by_account': 0})
        return action
