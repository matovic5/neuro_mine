.. _home:

=========================
Neuro-MINE Documentation
=========================

.. image:: https://img.shields.io/pypi/v/neuro-mine
   :target: https://pypi.org/project/neuro-mine/
   :alt: PyPI - Version

.. image:: https://img.shields.io/github/license/matovic5/neuro_mine
   :target: https://github.com/matovic5/neuro_mine/blob/main/LICENSE.txt
   :alt: GitHub License


**Neuro-MINE** (Model Identification of Neural Encoding) is a tool for analyzing neural response data
and making statistical inferences.

Neuro-MINE allows users to train a flexible, convolutional neural network (CNN)
to analyze experimental datasets containing neural activity and corresponding predictors
(e.g., behavioral responses).

It also allows for predictions of neural responses from a previously fit model for hypothesis generation.

------------

Quick Start
==============

Create an environment using Python v3.9:

.. code-block:: bash

   conda create -n mine python=3.12

Activate environment

.. code-block:: bash

   conda activate mine

Install/upgrade Neuro-MINE from PyPi

.. code-block:: bash

    pip install -U neuro_mine

------------

Links
========

- Source code: https://github.com/matovic5/neuro_mine
- PyPI: https://pypi.org/project/neuro-mine/
- Issue tracker: https://github.com/matovic5/neuro_mine/issues

------------

About the Project
====================

Neuro-MINE was created for neuroscientists by neuroscientists.

If you use this package in your research, please consider citing:

.. code-block:: text

   Costabile JD, Balakrishnan KA, Schwinn S, Haesemeyer M. Model discovery to link neural activity to behavioral tasks. Elife. 2023 Jun 6;12:e83289. doi: 10.7554/eLife.83289. PMID: 37278516; PMCID: PMC10310322. https://elifesciences.org/articles/83289


.. note::
   This documentation is a work in progress. Contributions and feedback are welcome.
   
   .. toctree::
   :maxdepth: 2
   :caption: Contents
   
   use_cases
   data_requirements
   training_module
   prediction_module
   advanced_usage