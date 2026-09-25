# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestProductSheet(TransactionCase):

    def setUp(self):
        super(TestProductSheet, self).setUp()
        self.tmpl = self.env['product.template'].create({'name': 'Monitor Teste'})

    def test_auto_is_accessory_without_data(self):
        self.assertEqual(self.tmpl.dgt_sheet_type, 'auto')
        self.assertEqual(self.tmpl.dgt_sheet_type_effective, 'accessory')

    def test_auto_is_equipment_with_specs(self):
        self.tmpl.write({'dgt_spec_ids': [(0, 0, {'name': 'Tela', 'value': '12"'})]})
        self.assertEqual(self.tmpl.dgt_sheet_type_effective, 'equipment')

    def test_auto_is_equipment_with_anvisa(self):
        self.tmpl.dgt_anvisa_reg = '10349000512'
        self.assertEqual(self.tmpl.dgt_sheet_type_effective, 'equipment')

    def test_forced_type_wins(self):
        self.tmpl.write({'dgt_anvisa_reg': '1', 'dgt_sheet_type': 'accessory'})
        self.assertEqual(self.tmpl.dgt_sheet_type_effective, 'accessory')

    def test_specs_ordered_and_visible_on_variant(self):
        self.tmpl.write({'dgt_spec_ids': [
            (0, 0, {'sequence': 20, 'name': 'B', 'value': '2'}),
            (0, 0, {'sequence': 10, 'name': 'A', 'value': '1'}),
        ]})
        variant = self.tmpl.product_variant_id
        self.assertEqual(variant.dgt_spec_ids.mapped('name'), ['A', 'B'])
        self.assertEqual(variant.dgt_sheet_type_effective, 'equipment')
