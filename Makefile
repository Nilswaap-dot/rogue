# SPDX-FileCopyrightText: 2021 Forschungs- und Entwicklungszentrum Fachhochschule Kiel GmbH
# 
# SPDX-License-Identifier: GPL-3.0-or-later

# virtualenv environment.
VENV?=.venv
ifeq ($(OS), Windows_NT)
	BIN?=$(VENV)\Scripts
else
	BIN?=$(VENV)/bin
endif
PYTHON?=$(BIN)/python
PIP?=$(BIN)/pip
PYTEST?=$(BIN)/pytest

.PHONY: default
default: venv
	$(PYTEST) -vv tests/

.PHONY: venv
venv:
	pip install virtualenv
ifeq ($(OS), Windows_NT)
	if NOT exist $(VENV) virtualenv $(VENV)
else
	[ -d $(VENV) ] || virtualenv $(VENV)
endif
	$(PIP) install -r requirements.txt
	$(PYTHON) setup.py install
