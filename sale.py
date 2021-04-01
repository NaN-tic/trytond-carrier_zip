# This file is part of the carrier_zip module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.transaction import Transaction


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    def _get_carrier_selection_pattern(self):
        pattern = super(Sale, self)._get_carrier_selection_pattern()
        if self.shipment_address:
            pattern['shipment_postal_code'] = self.shipment_address.postal_code
        return pattern

    def _get_carrier_context(self):
        context = super(Sale, self)._get_carrier_context()
        if self.carrier and self.carrier.carrier_cost_method == 'grid':
            context['shipment_postal_code'] = (self.shipment_address
                and self.shipment_address.postal_code or None)
        return context

    def create_shipment(self, shipment_type):
        context = {}
        if self.carrier:
            context = self._get_carrier_context()
        with Transaction().set_context(context):
            return super(Sale, self).create_shipment(shipment_type)
