# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestCompanyPalette(TransactionCase):

    def setUp(self):
        super(TestCompanyPalette, self).setUp()
        self.company = self.env['res.company'].create({'name': 'Empresa Teste Paleta'})

    def test_palette_defaults_on_new_company(self):
        pal = self.company.dgt_proposal_palette()
        self.assertEqual(pal['primary'], '#2E3A8C')
        self.assertEqual(pal['accent'], '#F0851E')

    def test_custom_colors_produce_expected_tints(self):
        self.company.write({'dgt_color_primary': '#000000', 'dgt_color_accent': '#000000'})
        pal = self.company.dgt_proposal_palette()
        self.assertEqual(pal['primary'], '#000000')
        self.assertEqual(pal['primary_tint'], '#F0F0F0')
        self.assertEqual(pal['primary_soft'], '#D9D9D9')
        self.assertEqual(pal['accent_tint'], '#E6E6E6')

    def test_invalid_primary_color_raises(self):
        with self.assertRaises(ValidationError):
            self.company.write({'dgt_color_primary': 'red'})

    def test_invalid_accent_color_raises(self):
        with self.assertRaises(ValidationError):
            self.company.write({'dgt_color_accent': '#12345'})

    def test_empty_colors_fall_back_to_defaults_in_palette(self):
        self.company.write({'dgt_color_primary': False, 'dgt_color_accent': False})
        pal = self.company.dgt_proposal_palette()
        self.assertEqual(pal['primary'], '#2E3A8C')
        self.assertEqual(pal['accent'], '#F0851E')

    def test_short_name_field_empty_by_default(self):
        self.assertFalse(self.company.dgt_short_name)
