# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .amount_text import amount_to_text_ptbr
from .res_partner import CUSTOMER_TYPES


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    dgt_is_proposal = fields.Boolean(string='Proposta Comercial', copy=True)
    dgt_customer_type = fields.Selection(CUSTOMER_TYPES, string='Tipo de cliente', default='private')
    dgt_include_cover = fields.Boolean(string='Incluir capa', default=True)
    dgt_bid_ref = fields.Char(string='Ref. Pregão/Processo')
    dgt_delivery_days = fields.Integer(string='Prazo de entrega (dias)')
    dgt_freight = fields.Selection([('cif', 'CIF (por conta do fornecedor)'), ('fob', 'FOB (por conta do cliente)')], string='Frete')
    dgt_installation = fields.Boolean(string='Instalação inclusa')
    dgt_installation_note = fields.Char(string='Obs. instalação')
    dgt_training = fields.Boolean(string='Treinamento incluso')
    dgt_training_note = fields.Char(string='Obs. treinamento')
    dgt_offer_preventive = fields.Boolean(string='Oferecer contrato de preventiva')
    dgt_preventive_value = fields.Monetary(string='Valor da preventiva', currency_field='currency_id')
    dgt_preventive_periodicity = fields.Selection([
        ('monthly', 'Mensal'), ('quarterly', 'Trimestral'),
        ('semiannual', 'Semestral'), ('annual', 'Anual'),
    ], string='Periodicidade da preventiva', default='monthly')
    dgt_preventive_note = fields.Text(string='Escopo da preventiva')
    dgt_amount_total_text = fields.Char(string='Total por extenso', compute='_compute_dgt_amount_total_text')
    dgt_max_warranty_months = fields.Integer(string='Maior garantia (meses)', compute='_compute_dgt_max_warranty_months')

    @api.depends('amount_total')
    def _compute_dgt_amount_total_text(self):
        for order in self:
            order.dgt_amount_total_text = amount_to_text_ptbr(order.amount_total)

    @api.depends('order_line.product_id')
    def _compute_dgt_max_warranty_months(self):
        for order in self:
            months = order.order_line.mapped('product_id.dgt_warranty_months')
            order.dgt_max_warranty_months = max(months) if months else 0

    @api.onchange('partner_id')
    def _onchange_dgt_partner_type(self):
        if self.partner_id:
            self.dgt_customer_type = self.partner_id.commercial_partner_id.dgt_customer_type or 'private'

    @api.model
    def create(self, vals):
        if vals.get('partner_id') and 'dgt_customer_type' not in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            vals['dgt_customer_type'] = partner.commercial_partner_id.dgt_customer_type or 'private'
        return super(SaleOrder, self).create(vals)

    @api.multi
    def action_print_proposal(self):
        return self.env.ref('dgt_sale.action_dgt_proposal_report').report_action(self)
