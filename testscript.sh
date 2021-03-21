#!/bin/bash

rm .coverage
python manage.py test sap.tests:AdminAllyTableFeatureTests
# python manage.py test
