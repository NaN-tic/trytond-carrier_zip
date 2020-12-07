# This file is part of the carrier_zip module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import carrier
from . import sale


def register():
    Pool.register(
        carrier.CarrierSelection,
        sale.Sale,
        module='carrier_zip', type_='model')
