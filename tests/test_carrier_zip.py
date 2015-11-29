#!/usr/bin/env python
# This file is part of the carrier_zip module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class CarrierZipTestCase(ModuleTestCase):
    'Test Carrier Zip module'
    module = 'carrier_zip'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        CarrierZipTestCase))
    return suite

