# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

RISK_CLASSES = [('I', 'Classe I'), ('II', 'Classe II'), ('III', 'Classe III'), ('IV', 'Classe IV')]

SHEET_PREFIX = 'dgt_'


def _is_sheet_only(vals):
    return bool(vals) and all(key.startswith(SHEET_PREFIX) for key in vals)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dgt_brand = fields.Char(string='Marca')
    dgt_model = fields.Char(string='Modelo')
    dgt_manufacturer = fields.Char(string='Fabricante')
    dgt_origin_country_id = fields.Many2one('res.country', string='Origem')
    dgt_anvisa_reg = fields.Char(string='Registro Anvisa')
    dgt_risk_class = fields.Selection(RISK_CLASSES, string='Classe de risco')
    dgt_warranty_months = fields.Integer(string='Garantia (meses)')
    dgt_clinical_description = fields.Html(string='Descrição / Aplicações')
    dgt_spec_ids = fields.One2many('dgt.product.spec', 'product_tmpl_id', string='Especificações técnicas', copy=True)
    dgt_included_items = fields.Text(string='Acompanha')
    dgt_sheet_type = fields.Selection([
        ('auto', 'Automático'),
        ('equipment', 'Equipamento (ficha completa)'),
        ('accessory', 'Acessório / consumível (compacta)'),
    ], string='Tipo de ficha', default='auto', required=True)
    dgt_sheet_type_effective = fields.Selection([
        ('equipment', 'Equipamento'),
        ('accessory', 'Acessório'),
    ], string='Ficha usada', compute='_compute_dgt_sheet_type_effective')

    @api.depends('dgt_sheet_type', 'dgt_spec_ids', 'dgt_anvisa_reg')
    def _compute_dgt_sheet_type_effective(self):
        for tmpl in self:
            if tmpl.dgt_sheet_type != 'auto':
                tmpl.dgt_sheet_type_effective = tmpl.dgt_sheet_type
            elif tmpl.dgt_spec_ids or tmpl.dgt_anvisa_reg:
                tmpl.dgt_sheet_type_effective = 'equipment'
            else:
                tmpl.dgt_sheet_type_effective = 'accessory'

    @api.multi
    def write(self, vals):
        user = self.env.user
        if (_is_sheet_only(vals)
                and not self.check_access_rights('write', raise_exception=False)
                and user.has_group('dgt_sale.group_product_sheet_editor')):
            res = super(ProductTemplate, self.sudo()).write(vals)
            for tmpl in self.sudo():
                tmpl.message_post(body=_('Ficha técnica atualizada por %s') % user.name)
            return res
        return super(ProductTemplate, self).write(vals)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def write(self, vals):
        if (_is_sheet_only(vals)
                and not self.check_access_rights('write', raise_exception=False)):
            return self.mapped('product_tmpl_id').write(vals)
        return super(ProductProduct, self).write(vals)
