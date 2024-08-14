import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.account.tests.tools import create_chart, create_fiscalyear
from trytond.modules.account_invoice.tests.tools import \
    set_fiscalyear_invoice_sequences
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install carrier_zip module
        activate_modules('carrier_zip')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)

        # Create some postal codes
        Country = Model.get('country.country')
        PostalCode = Model.get('country.postal_code')
        country = Country(name='Country')
        country.save()
        PostalCode.save([
            PostalCode(country=country, postal_code=str(i)) for i in range(10)
        ])

        # Create customer
        Party = Model.get('party.party')
        customer = Party(name='Customer')
        address, = customer.addresses
        postal_code, = PostalCode.find([('postal_code', '=', '2')])
        address.postal_code = postal_code.postal_code
        customer.save()
        other_customer = Party(name='Other Customer')
        address, = other_customer.addresses
        postal_code, = PostalCode.find([('postal_code', '=', '7')])
        address.postal_code = postal_code.postal_code
        other_customer.save()

        # Create product
        ProductUom = Model.get('product.uom')
        ProductTemplate = Model.get('product.template')
        Product = Model.get('product.product')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        product = Product()
        template = ProductTemplate()
        template.name = 'Product'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('20')
        template.save()
        product.template = template
        product.save()
        carrier_product = Product()
        carrier_template = ProductTemplate()
        carrier_template.name = 'Carrier Product'
        carrier_template.default_uom = unit
        carrier_template.type = 'service'
        carrier_template.salable = True
        carrier_template.list_price = Decimal('3')
        carrier_template.save()
        carrier_product.template = carrier_template
        carrier_product.save()

        # Create carrier
        Carrier = Model.get('carrier')
        carrier = Carrier()
        party = Party(name='Carrier')
        party.save()
        carrier.party = party
        carrier.carrier_product = carrier_product
        carrier.save()

        # Create a selection for postal_code from 1 to 5
        CarrierSelection = Model.get('carrier.selection')
        csc = CarrierSelection(carrier=carrier)
        csc.start_postal_code, = PostalCode.find([('postal_code', '=', '1')])
        csc.end_postal_code, = PostalCode.find([('postal_code', '=', '5')])
        csc.save()

        # The carrier is selected for customer
        Sale = Model.get('sale.sale')
        sale = Sale()
        sale.party = customer
        self.assertEqual(sale.carrier, carrier)

        # But it's not selected for customers outside the range
        sale.party = other_customer
        sale.carrier
