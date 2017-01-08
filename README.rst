========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |codecov|
        | |codeclimate|
    * - package
      - |version| |downloads| |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/python-robin-srv/badge/?style=flat
    :target: https://readthedocs.org/projects/python-robin-srv
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/RobertDeRose/python-robin-srv.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/RobertDeRose/python-robin-srv

.. |requires| image:: https://requires.io/github/RobertDeRose/python-robin-srv/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/RobertDeRose/python-robin-srv/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/RobertDeRose/python-robin-srv/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/RobertDeRose/python-robin-srv

.. |codeclimate| image:: https://codeclimate.com/github/RobertDeRose/python-robin-srv/badges/gpa.svg
   :target: https://codeclimate.com/github/RobertDeRose/python-robin-srv
   :alt: CodeClimate Quality Status

.. |version| image:: https://img.shields.io/pypi/v/robin-srv.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/robin-srv

.. |downloads| image:: https://img.shields.io/pypi/dm/robin-srv.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/robin-srv

.. |wheel| image:: https://img.shields.io/pypi/wheel/robin-srv.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/robin-srv

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/robin-srv.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/robin-srv

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/robin-srv.svg?style=flat
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/robin-srv


.. end-badges

A utility library to help with client-side load balancing based on SRV records.

* Free software: BSD license

Installation
============

::

    pip install robin-srv

Documentation
=============

https://python-robin-srv.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
