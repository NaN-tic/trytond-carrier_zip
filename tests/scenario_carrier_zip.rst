====================
Carrier Zip Scenario
====================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences
    >>> today = datetime.date.today()

Install carrier_zip module::

    >>> config = activate_modules('carrier_zip')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']

Create some postal codes::

    >>> Country = Model.get('country.country')
    >>> PostalCode = Model.get('country.postal_code')
    >>> country = Country(name='Country')
    >>> country.save()
    >>> PostalCode.save([PostalCode(country=country, postal_code=str(i))
    ...       for i in range(10)])

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> address, = customer.addresses
    >>> postal_code, = PostalCode.find([('postal_code', '=', '2')])
    >>> address.postal_code = postal_code.postal_code
    >>> customer.save()
    >>> other_customer = Party(name='Other Customer')
    >>> address, = other_customer.addresses
    >>> postal_code, = PostalCode.find([('postal_code', '=', '7')])
    >>> address.postal_code = postal_code.postal_code
    >>> other_customer.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'Product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.salable = True
    >>> template.list_price = Decimal('20')
    >>> template.save()
    >>> product.template = template
    >>> product.save()
    >>> carrier_product = Product()
    >>> carrier_template = ProductTemplate()
    >>> carrier_template.name = 'Carrier Product'
    >>> carrier_template.default_uom = unit
    >>> carrier_template.type = 'service'
    >>> carrier_template.salable = True
    >>> carrier_template.list_price = Decimal('3')
    >>> carrier_template.save()
    >>> carrier_product.template = carrier_template
    >>> carrier_product.save()

Create carrier::

    >>> Carrier = Model.get('carrier')
    >>> carrier = Carrier()
    >>> party = Party(name='Carrier')
    >>> party.save()
    >>> carrier.party = party
    >>> carrier.carrier_product = carrier_product
    >>> carrier.save()

Create a selection for postal_code from 1 to 5::

    >>> CarrierSelection = Model.get('carrier.selection')
    >>> csc = CarrierSelection(carrier=carrier)
    >>> csc.start_postal_code, = PostalCode.find([('postal_code', '=', '1')])
    >>> csc.end_postal_code, = PostalCode.find([('postal_code', '=', '5')])
    >>> csc.save()

The carrier is selected for customer::

    >>> Sale = Model.get('sale.sale')
    >>> sale = Sale()
    >>> sale.party = customer
    >>> sale.carrier == carrier
    True

But it's not selected for customers outside the range::

    >>> sale.party = other_customer
    >>> sale.carrier
