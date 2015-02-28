# This file is part of the carrier_zip module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['Sale']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'
    carrier_domain = fields.Function(fields.One2Many('carrier', None,
            'Carrier Domain', depends=['shipment_address', 'party']),
        'on_change_with_carrier_domain')

    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()
        if 'shipment_address' not in cls.lines.on_change:
            cls.lines.on_change.add('shipment_address')
        if 'shipment_address' not in cls.lines.depends:
            cls.lines.depends.append('shipment_address')
        cls._error_messages.update({
                'zip_unavailable': 'The zip "%s" is unavailable for the '
                    'carrier "%s".',
                })
        if hasattr(cls, 'carrier'):
            if 'shipment_address' not in cls.carrier.on_change:
                cls.carrier.on_change.add('shipment_address')
            if 'shipment_address' not in cls.carrier.depends:
                cls.carrier.depends.append('shipment_address')
            carrier_domain = ('id', 'in', Eval('carrier_domain', []))
            if carrier_domain not in cls.carrier.domain:
                cls.carrier.domain.append(carrier_domain)
            if 'carrier_domain' not in cls.carrier.depends:
                cls.carrier.depends.append('carrier_domain')

    @fields.depends('shipment_address', 'party')
    def on_change_with_carrier_domain(self, name=None):
        Carrier = Pool().get('carrier')
        shipment_zip = (self.shipment_address and self.shipment_address.zip
            or '')
        carrier_ids = []
        carriers = Carrier.search([])
        for carrier in carriers:
            for carrier_zip in carrier.zips:
                if shipment_zip:
                    try:
                        zip_ = int(shipment_zip)
                        start_zip = int(carrier_zip.start_zip)
                        end_zip = int(carrier_zip.end_zip)
                    except:
                        break
                    if (start_zip <= zip_ <= end_zip):
                        carrier_ids.append(carrier.id)
                        break
                else:
                    carrier_ids.append(carrier.id)
                    break
            else:
                if not carrier.zips:
                    carrier_ids.append(carrier.id)
        return carrier_ids

    def _get_carrier_context(self):
        context = super(Sale, self)._get_carrier_context()
        if self.carrier and self.carrier.carrier_cost_method == 'grid':
            context['shipment_zip'] = (self.shipment_address
                and self.shipment_address.zip or None)
        return context

    def check_for_quotation(self):
        res = super(Sale, self).check_for_quotation()
        shipment_zip = (self.shipment_address and self.shipment_address.zip
            or '')
        carrier = self.carrier
        if not carrier or not carrier.zips:
            return res
        if (carrier and shipment_zip):
            for carrier_zip in carrier.zips:
                if (int(carrier_zip.start_zip) <= int(shipment_zip)
                        <= int(carrier_zip.end_zip)):
                    break
            else:
                self.raise_user_warning('%s.on_change_carrier' % self,
                    'zip_unavailable', (shipment_zip, carrier.party.rec_name))
        return res

    def create_shipment(self, shipment_type):
        with Transaction().set_context(self._get_carrier_context()):
            return super(Sale, self).create_shipment(shipment_type)
