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

Create some zip codes::

    >>> Country = Model.get('country.country')
    >>> Zip = Model.get('country.zip')
    >>> country = Country(name='Country')
    >>> country.save()
    >>> Zip.save([Zip(country=country, zip=str(i)) for i in range(10)])

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> address, = customer.addresses
    >>> zip, = Zip.find([('zip', '=', '2')])
    >>> address.zip = zip.zip
    >>> customer.save()
    >>> other_customer = Party(name='Other Customer')
    >>> address, = other_customer.addresses
    >>> zip, = Zip.find([('zip', '=', '7')])
    >>> address.zip = zip.zip
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
    >>> template.lead_time = datetime.timedelta(0)
    >>> template.list_price = Decimal('20')
    >>> template.cost_price = Decimal('8')
    >>> template.account_revenue = revenue
    >>> template.save()
    >>> product.template = template
    >>> product.save()
    >>> carrier_product = Product()
    >>> carrier_template = ProductTemplate()
    >>> carrier_template.name = 'Carrier Product'
    >>> carrier_template.default_uom = unit
    >>> carrier_template.type = 'service'
    >>> carrier_template.salable = True
    >>> carrier_template.lead_time = datetime.timedelta(0)
    >>> carrier_template.list_price = Decimal('3')
    >>> carrier_template.cost_price = Decimal(0)
    >>> carrier_template.account_revenue = revenue
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

Create a selection for zips from 1 to 5::

    >>> CarrierSelection = Model.get('carrier.selection')
    >>> csc = CarrierSelection(carrier=carrier)
    >>> csc.start_zip, = Zip.find([('zip', '=', '1')])
    >>> csc.end_zip, = Zip.find([('zip', '=', '5')])
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
