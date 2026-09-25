# -*- coding: utf-8 -*-
from odoo import fields, models

CUSTOMER_TYPES = [('private', 'Privado'), ('public', 'Público')]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    dgt_customer_type = fields.Selection(CUSTOMER_TYPES, string='Tipo de cliente (proposta)', default='private')
