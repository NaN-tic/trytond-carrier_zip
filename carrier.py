# This file is part of the carrier_zip module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta

__metaclass__ = PoolMeta
__all__ = ['CarrierZip', 'Carrier']


class CarrierZip(ModelSQL, ModelView):
    'Carrier Zip'
    __name__ = 'carrier.zip'
    carrier = fields.Many2One('carrier', 'Carrier', required=True, select=True)
    start_zip = fields.Char('Start Zip', required=True)
    end_zip = fields.Char('End Zip', required=True)

    @classmethod
    def __setup__(cls):
        super(CarrierZip, cls).__setup__()
        cls._error_messages.update({
                'wrong_zip': 'Can\'t validate this zip. You must set it as an '
                    'integer number.'
                })

    @classmethod
    def validate(cls, records):
        super(CarrierZip, cls).validate(records)
        for record in records:
            record.check_zip_code()

    def check_zip_code(self):
        try:
            int(self.start_zip)
            int(self.end_zip)
        except:
            self.raise_user_error('wrong_zip')


class Carrier:
    __name__ = 'carrier'
    zips = fields.One2Many('carrier.zip', 'carrier', 'Carrier Zips')

    @staticmethod
    def get_carriers_from_zip(zip_code, carriers=None):
        CarrierZip = Pool().get('carrier.zip')

        domain = [
            ('start_zip', '<=', zip_code),
            ('end_zip', '>=', zip_code),
            ]
        if carriers:
            domain.append(
                ('carrier.id', 'in', [c.id for c in carriers]))
        carrier_zips = CarrierZip.search(domain)
        return [c.carrier for c in carrier_zips]
