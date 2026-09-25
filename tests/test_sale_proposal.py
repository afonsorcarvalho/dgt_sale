# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.dgt_sale.models.res_company import DEFAULT_DECLARATIONS, NEW_LI, OLD_LI


@tagged('post_install', '-at_install')
class TestSaleProposal(TransactionCase):

    def setUp(self):
        super(TestSaleProposal, self).setUp()
        self.public = self.env['res.partner'].create({'name': 'Prefeitura Teste', 'dgt_customer_type': 'public'})
        self.private = self.env['res.partner'].create({'name': 'Clínica Teste'})
        self.order = self.env['sale.order'].create({'partner_id': self.private.id})

    def test_partner_default_private(self):
        self.assertEqual(self.private.dgt_customer_type, 'private')

    def test_onchange_partner_copies_type(self):
        order = self.env['sale.order'].new({'partner_id': self.public.id})
        order._onchange_dgt_partner_type()
        self.assertEqual(order.dgt_customer_type, 'public')

    def test_create_copies_type_from_partner(self):
        order = self.env['sale.order'].create({'partner_id': self.public.id})
        self.assertEqual(order.dgt_customer_type, 'public')

    def test_amount_text_empty_order(self):
        self.assertEqual(self.order.dgt_amount_total_text, 'zero reais')

    def test_max_warranty_zero_without_lines(self):
        self.assertEqual(self.order.dgt_max_warranty_months, 0)

    def test_print_action(self):
        action = self.order.action_print_proposal()
        self.assertEqual(action.get('report_name'), 'dgt_sale.dgt_proposal_report')

    def test_company_defaults(self):
        company = self.env.ref('base.main_company')
        self.assertTrue(company.dgt_proposal_letter)
        self.assertTrue(company.dgt_public_declarations)

    def test_proposal_menu_action_domain(self):
        action = self.env.ref('dgt_sale.action_dgt_proposals')
        self.assertIn('dgt_is_proposal', action.domain)

    def test_fix_validity_declaration_replaces_old_text(self):
        company = self.env.ref('base.main_company')
        company.dgt_public_declarations = '<p>Declaramos que:</p><ul>' + OLD_LI + '</ul>'
        self.env['res.company']._dgt_fix_validity_declaration()
        self.assertNotIn('60 (sessenta)', company.dgt_public_declarations)
        self.assertIn(NEW_LI, company.dgt_public_declarations)

    def test_default_declarations_no_fixed_validity(self):
        self.assertNotIn('60 (sessenta)', DEFAULT_DECLARATIONS)
