ahocode
==================
This repo is a pure python implementation for `pyahocorasick <https://github.com/WojciechMula/pyahocorasick>`_, inspired by `abusix/ahocorapy <https://github.com/abusix/ahocorapy>`_.


Installation
-------------------

Requirements
###################
* Python 3.8 or later

.. code-block:: bash

    pip install ahocode

Documentation
---------------------------
ahocode is a fallback library for pyahocorasick, so the ``Automaton`` class and its methods
have same names and parameters.

Below listed are the implemented classes and methods.

Classes
##########

* ``Automaton``

Methods for Automaton class
###############################

* ``add_word``
* ``get``
* ``clear``
* ``exists``
* ``find_all``
* ``items``
* ``make_automaton``
* ``iter``
* ``keys``
* ``values``
* ``__getstate__``
* ``__setstate__``
* ``__len__``
* ``__contains__``

For documentation please refer to: https://pyahocorasick.readthedocs.io/en/latest