# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    dgt_include_cover = fields.Boolean(string='Incluir capa', default=True)
