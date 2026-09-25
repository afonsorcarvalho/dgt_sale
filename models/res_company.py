# -*- coding: utf-8 -*-
from odoo import api, fields, models

DEFAULT_LETTER = (
    '<p>Prezados,</p>'
    '<p>Agradecemos a oportunidade de apresentar nossa proposta. A Diagnóstica atua no fornecimento, '
    'instalação e manutenção de equipamentos médico-hospitalares, com assistência técnica própria em '
    'São Luís e equipe treinada pelos fabricantes que representamos.</p>'
    '<p>Nas páginas seguintes apresentamos o resumo do investimento, a ficha técnica de cada item e as '
    'condições comerciais. Ficamos à disposição para demonstrações e esclarecimentos.</p>'
)
DEFAULT_DIFFERENTIALS = (
    '<ul>'
    '<li>Assistência técnica própria em São Luís</li>'
    '<li>Manutenção preventiva, corretiva e calibração</li>'
    '<li>Técnicos treinados pelos fabricantes</li>'
    '<li>Instalação e treinamento operacional da equipe</li>'
    '</ul>'
)
OLD_LI = '<li>A presente proposta tem validade de 60 (sessenta) dias a contar da data de sua emissão.</li>'
NEW_LI = '<li>A presente proposta tem a validade indicada nas condições comerciais.</li>'

DEFAULT_DECLARATIONS = (
    '<p>Declaramos que:</p>'
    '<ul>'
    '<li>Nos preços propostos estão inclusos todos os impostos, taxas, fretes, seguros e demais encargos '
    'incidentes sobre o fornecimento.</li>'
    '<li>Os produtos ofertados possuem registro vigente na Anvisa, conforme indicado em cada ficha técnica.</li>'
    + NEW_LI +
    '<li>Cumprimos plenamente os requisitos de habilitação exigidos no edital.</li>'
    '</ul>'
)


class ResCompany(models.Model):
    _inherit = 'res.company'

    dgt_proposal_letter = fields.Html(string='Carta de apresentação', default=DEFAULT_LETTER)
    dgt_proposal_differentials = fields.Html(string='Diferenciais', default=DEFAULT_DIFFERENTIALS)
    dgt_afe_anvisa = fields.Char(string='AFE Anvisa')
    dgt_bank_info = fields.Text(string='Dados bancários')
    dgt_public_declarations = fields.Html(string='Declarações (cliente público)', default=DEFAULT_DECLARATIONS)

    @api.model
    def _dgt_fix_validity_declaration(self):
        """Replace the old fixed-validity sentence with one that defers to the
        commercial conditions block, in existing company rows that still hold
        the pre-fix default text. Leaves any other user edits intact."""
        companies = self.search([])
        for company in companies:
            text = company.dgt_public_declarations or ''
            if OLD_LI in text:
                company.dgt_public_declarations = text.replace(OLD_LI, NEW_LI)
