# -*- coding: utf-8 -*-
"""Brazilian Portuguese currency amount in words.

num2words(pt_BR, to='currency') separates every thousand group with a comma
("um milhão, duzentos e cinquenta mil reais"). pt-BR rule: groups are joined
by a space, except the last non-zero group which is joined by " e " when it is
below 100 or a round hundred.
"""
import logging
from decimal import Decimal, ROUND_HALF_UP

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    num2words = None
    _logger.warning('num2words is not installed; amount_to_text_ptbr will return an empty string.')


def _last_nonzero_group(integer):
    while integer and integer % 1000 == 0:
        integer //= 1000
    return integer % 1000


def amount_to_text_ptbr(amount):
    if num2words is None:
        return ''
    value = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    integer = int(value)
    text = num2words(value, lang='pt_BR', to='currency')
    if integer == 0 and value != 0:
        prefix = 'zero reais e '
        if text.startswith(prefix):
            text = text[len(prefix):]
        return text
    parts = text.split(', ')
    if len(parts) == 1:
        return text
    last = _last_nonzero_group(integer)
    last_sep = ' e ' if (last < 100 or last % 100 == 0) else ' '
    return ' '.join(parts[:-1]) + last_sep + parts[-1]
