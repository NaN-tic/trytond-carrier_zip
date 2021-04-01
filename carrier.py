# This file is part of the carrier_zip module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import If, Bool, Eval


class CarrierSelection(metaclass=PoolMeta):
    __name__ = 'carrier.selection'

    start_postal_code = fields.Many2One('country.postal_code',
        'Start Postal Code', domain=[
            If(Bool(Eval('to_country')),
                ('country', '=', Eval('to_country')),
                (),
                )],
        depends=['to_country'])
    end_postal_code = fields.Many2One('country.postal_code', 'End Postal Code',
        domain=[
            If(Bool(Eval('to_country')),
                ('country', '=', Eval('to_country')),
                (),
                )],
        depends=['to_country'])

    @classmethod
    def __register__(cls, module):
        # Migration from 5.8: rename zip to postal_code
        table_h = cls.__table_handler__(module)
        table_h.column_rename('start_zip', 'start_postal_code')
        table_h.column_rename('end_zip', 'end_postal_code')
        super().__register__(module)

    def match(self, pattern):
        if 'shipment_postal_code' in pattern:
            pattern = pattern.copy()
            shipment_postal_code = pattern.pop('shipment_postal_code')
            if ((self.start_postal_code or self.end_postal_code)
                    and shipment_postal_code):
                start_postal_code, end_postal_code = None, None
                try:
                    postal_code = int(shipment_postal_code)
                    if self.start_postal_code:
                        start_postal_code = int(self.start_postal_code.postal_code)
                    if self.end_postal_code:
                        end_postal_code = int(self.end_postal_code.postal_code)
                except ValueError:
                    pass
                if start_postal_code and postal_code < start_postal_code:
                    return False
                if end_postal_code and postal_code > end_postal_code:
                    return False
        return super(CarrierSelection, self).match(pattern)
