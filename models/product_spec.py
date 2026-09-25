# -*- coding: utf-8 -*-
from odoo import fields, models


class DgtProductSpec(models.Model):
    _name = 'dgt.product.spec'
    _description = 'Especificação técnica de produto'
    _order = 'sequence, id'

    product_tmpl_id = fields.Many2one('product.template', string='Produto', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(default=10)
    group = fields.Char(string='Grupo')
    name = fields.Char(string='Atributo', required=True)
    value = fields.Char(string='Valor', required=True)
