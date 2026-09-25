# -*- coding: utf-8 -*-
from lxml import etree

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestProductAccess(TransactionCase):

    def setUp(self):
        super(TestProductAccess, self).setUp()
        self.tmpl = self.env['product.template'].create({'name': 'Desfibrilador Teste', 'list_price': 100.0})
        self.source = self.env['product.template'].create({
            'name': 'Fonte',
            'dgt_brand': 'Mindray',
            'dgt_anvisa_reg': '123',
            'dgt_spec_ids': [(0, 0, {'name': 'Tela', 'value': '12"', 'group': 'Físico'})],
        })
        salesman = self.env.ref('sales_team.group_sale_salesman')
        editor = self.env.ref('dgt_sale.group_product_sheet_editor')
        self.seller = self.env['res.users'].create({
            'name': 'Vendedor Ficha', 'login': 'vendedor_ficha_test',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id, salesman.id, editor.id])],
        })
        # base.group_user only: no sales group at all, so no editor group is implied either.
        self.plain = self.env['res.users'].create({
            'name': 'Vendedor Sem Ficha', 'login': 'vendedor_sem_ficha_test',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

    def test_editor_writes_sheet_fields_on_template(self):
        self.tmpl.sudo(self.seller).write({
            'dgt_brand': 'Mindray',
            'dgt_spec_ids': [(0, 0, {'name': 'Bateria', 'value': '4 h'})],
        })
        self.assertEqual(self.tmpl.dgt_brand, 'Mindray')
        self.assertEqual(self.tmpl.dgt_spec_ids.mapped('name'), ['Bateria'])

    def test_editor_writes_sheet_fields_on_variant(self):
        self.tmpl.product_variant_id.sudo(self.seller).write({'dgt_model': 'D3'})
        self.assertEqual(self.tmpl.dgt_model, 'D3')

    def test_editor_cannot_write_price(self):
        with self.assertRaises(AccessError):
            self.tmpl.sudo(self.seller).write({'list_price': 1.0})

    def test_editor_cannot_mix_sheet_and_price(self):
        with self.assertRaises(AccessError):
            self.tmpl.sudo(self.seller).write({'dgt_brand': 'X', 'list_price': 1.0})
        self.assertFalse(self.tmpl.dgt_brand)

    def test_non_editor_cannot_write_sheet(self):
        with self.assertRaises(AccessError):
            self.tmpl.sudo(self.plain).write({'dgt_brand': 'X'})

    def test_chatter_logs_real_user(self):
        self.tmpl.sudo(self.seller).write({'dgt_brand': 'Mindray'})
        bodies = ' '.join(self.tmpl.message_ids.mapped('body'))
        self.assertIn('Vendedor Ficha', bodies)

    def test_copy_wizard(self):
        self.tmpl.write({'dgt_brand': 'Já tinha', 'dgt_spec_ids': [(0, 0, {'name': 'Velha', 'value': 'x'})]})
        wiz = self.env['dgt.copy.spec.wizard'].sudo(self.seller).with_context(
            active_model='product.product', active_id=self.tmpl.product_variant_id.id,
        ).create({'source_tmpl_id': self.source.id})
        self.assertEqual(wiz.target_tmpl_id, self.tmpl)
        wiz.action_copy()
        self.assertEqual(self.tmpl.dgt_spec_ids.mapped('name'), ['Tela'])
        self.assertEqual(self.tmpl.dgt_brand, 'Já tinha')      # non-empty kept
        self.assertEqual(self.tmpl.dgt_anvisa_reg, '123')       # empty filled

    # F1 — dedicated sheet-edit form must be editable in the UI for a salesman
    # with no write ACL on product.template.

    def test_sheet_form_view_is_editable_for_editor(self):
        view = self.env.ref('dgt_sale.product_template_sheet_form')
        result = self.env['product.template'].sudo(self.seller).fields_view_get(
            view_id=view.id, view_type='form')
        arch = etree.fromstring(result['arch'].encode('utf-8') if isinstance(result['arch'], str) else result['arch'])
        self.assertNotEqual(arch.get('edit'), 'false')

    def test_action_dgt_edit_sheet_from_template(self):
        view = self.env.ref('dgt_sale.product_template_sheet_form')
        action = self.tmpl.action_dgt_edit_sheet()
        self.assertEqual(action['res_model'], 'product.template')
        self.assertEqual(action['res_id'], self.tmpl.id)
        self.assertEqual(action['views'], [(view.id, 'form')])
        self.assertEqual(action['target'], 'new')

    def test_action_dgt_edit_sheet_from_variant(self):
        view = self.env.ref('dgt_sale.product_template_sheet_form')
        action = self.tmpl.product_variant_id.action_dgt_edit_sheet()
        self.assertEqual(action['res_model'], 'product.template')
        self.assertEqual(action['res_id'], self.tmpl.id)
        self.assertEqual(action['views'], [(view.id, 'form')])
        self.assertEqual(action['target'], 'new')

    # F2 — explicit whitelist: a non-whitelisted key must never ride the sudo path.

    def test_non_whitelisted_key_not_sudoed(self):
        with self.assertRaises(AccessError):
            self.tmpl.sudo(self.seller).write({'dgt_brand': 'X', 'dgt_sheet_type_effective': 'equipment'})

    # F5 — negative variant-write tests.

    def test_variant_write_by_non_editor_raises(self):
        with self.assertRaises(AccessError):
            self.tmpl.product_variant_id.sudo(self.plain).write({'dgt_model': 'X'})

    def test_variant_write_mixed_sheet_and_price_raises(self):
        with self.assertRaises(AccessError):
            self.tmpl.product_variant_id.sudo(self.seller).write({'dgt_model': 'X', 'lst_price': 1.0})
