# -*- coding: utf-8 -*-
from odoo import api, fields, models

SCALAR_FIELDS = [
    'dgt_brand', 'dgt_model', 'dgt_manufacturer', 'dgt_origin_country_id',
    'dgt_anvisa_reg', 'dgt_risk_class', 'dgt_warranty_months',
    'dgt_clinical_description', 'dgt_included_items',
]


class DgtCopySpecWizard(models.TransientModel):
    _name = 'dgt.copy.spec.wizard'
    _description = 'Copiar ficha técnica de outro produto'

    @api.model
    def _default_target(self):
        model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if not active_id:
            return False
        if model == 'product.product':
            return self.env['product.product'].browse(active_id).product_tmpl_id
        if model == 'product.template':
            return self.env['product.template'].browse(active_id)
        return False

    target_tmpl_id = fields.Many2one('product.template', string='Produto destino', required=True, default=_default_target)
    source_tmpl_id = fields.Many2one('product.template', string='Copiar de', required=True)

    @api.multi
    def action_copy(self):
        self.ensure_one()
        source = self.source_tmpl_id.sudo()
        target = self.target_tmpl_id
        vals = {'dgt_spec_ids': [(5, 0, 0)] + [
            (0, 0, {'sequence': s.sequence, 'group': s.group, 'name': s.name, 'value': s.value})
            for s in source.dgt_spec_ids
        ]}
        for fname in SCALAR_FIELDS:
            if not target[fname] and source[fname]:
                value = source[fname]
                vals[fname] = value.id if fname.endswith('_id') else value
        target.write(vals)
        return {'type': 'ir.actions.act_window_close'}
