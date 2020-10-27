# This file is part of the carrier_zip module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import If, Bool, Eval

__all__ = ['CarrierSelection']


class CarrierSelection(metaclass=PoolMeta):
    __name__ = 'carrier.selection'

    start_zip = fields.Many2One('country.zip', 'Start Zip',
        domain=[
            If(Bool(Eval('to_country')),
                ('country', '=', Eval('to_country')),
                (),
                )],
        depends=['to_country'])
    end_zip = fields.Many2One('country.zip', 'End Zip',
        domain=[
            If(Bool(Eval('to_country')),
                ('country', '=', Eval('to_country')),
                (),
                )],
        depends=['to_country'])

    def match(self, pattern):
        if 'shipment_zip' in pattern:
            pattern = pattern.copy()
            shipment_zip = pattern.pop('shipment_zip')
            if (self.start_zip or self.end_zip) and shipment_zip:
                start_zip, end_zip = None, None
                try:
                    zip = int(shipment_zip)
                    if self.start_zip:
                        start_zip = int(self.start_zip.zip)
                    if self.end_zip:
                        end_zip = int(self.end_zip.zip)
                except ValueError:
                    pass
                if start_zip and zip < start_zip:
                    return False
                if end_zip and zip > end_zip:
                    return False
        return super(CarrierSelection, self).match(pattern)
