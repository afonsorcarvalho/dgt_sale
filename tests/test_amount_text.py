# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.dgt_sale.models.amount_text import amount_to_text_ptbr


@tagged('post_install', '-at_install')
class TestAmountText(TransactionCase):

    def test_values(self):
        cases = [
            (0.01, 'um centavo'),
            (1, 'um real'),
            (1000, 'mil reais'),
            (1100, 'mil e cem reais'),
            (1250, 'mil duzentos e cinquenta reais'),
            (124600, 'cento e vinte e quatro mil e seiscentos reais'),
            (38900.35, 'trinta e oito mil e novecentos reais e trinta e cinco centavos'),
            (1000000, 'um milhão de reais'),
            (1200000, 'um milhão e duzentos mil reais'),
            (1250000, 'um milhão duzentos e cinquenta mil reais'),
            (2345678.90, 'dois milhões trezentos e quarenta e cinco mil seiscentos e setenta e oito reais e noventa centavos'),
        ]
        for amount, expected in cases:
            self.assertEqual(amount_to_text_ptbr(amount), expected, 'amount %s' % amount)

    def test_zero(self):
        self.assertEqual(amount_to_text_ptbr(0), 'zero reais')
