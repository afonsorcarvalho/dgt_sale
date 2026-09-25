# -*- coding: utf-8 -*-
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

COLOR_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')
DEFAULT_COLOR_PRIMARY = '#2E3A8C'
DEFAULT_COLOR_ACCENT = '#F0851E'

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


def _mix_with_white(hex_color, ratio):
    hex_color = hex_color.lstrip('#')
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)
    red = round(red + (255 - red) * ratio)
    green = round(green + (255 - green) * ratio)
    blue = round(blue + (255 - blue) * ratio)
    return '#%02X%02X%02X' % (red, green, blue)


class ResCompany(models.Model):
    _inherit = 'res.company'

    dgt_color_primary = fields.Char(string='Cor principal', default=DEFAULT_COLOR_PRIMARY)
    dgt_color_accent = fields.Char(string='Cor de destaque', default=DEFAULT_COLOR_ACCENT)
    dgt_short_name = fields.Char(string='Nome curto (proposta)')
    dgt_proposal_letter = fields.Html(string='Carta de apresentação', default=DEFAULT_LETTER)
    dgt_proposal_differentials = fields.Html(string='Diferenciais', default=DEFAULT_DIFFERENTIALS)
    dgt_afe_anvisa = fields.Char(string='AFE Anvisa')
    dgt_bank_info = fields.Text(string='Dados bancários')
    dgt_public_declarations = fields.Html(string='Declarações (cliente público)', default=DEFAULT_DECLARATIONS)

    @api.constrains('dgt_color_primary', 'dgt_color_accent')
    def _check_dgt_colors(self):
        for company in self:
            for fname in ('dgt_color_primary', 'dgt_color_accent'):
                value = company[fname]
                if value and not COLOR_RE.match(value):
                    raise ValidationError(
                        _('%s deve ser uma cor hexadecimal no formato #RRGGBB.') % company._fields[fname].string
                    )

    def dgt_proposal_palette(self):
        self.ensure_one()
        primary = self.dgt_color_primary
        if not primary or not COLOR_RE.match(primary):
            primary = DEFAULT_COLOR_PRIMARY
        accent = self.dgt_color_accent
        if not accent or not COLOR_RE.match(accent):
            accent = DEFAULT_COLOR_ACCENT
        return {
            'primary': primary.upper(),
            'accent': accent.upper(),
            'primary_tint': _mix_with_white(primary, 0.94),
            'primary_soft': _mix_with_white(primary, 0.85),
            'accent_tint': _mix_with_white(accent, 0.90),
        }

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
