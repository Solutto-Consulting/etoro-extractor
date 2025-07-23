# Makefile for eToro Extractor

.PHONY: help install test clean lint format run

# Default target
help:
	@echo "eToro Extractor - Available commands:"
	@echo ""
	@echo "  install     - Install dependencies in virtual environment"
	@echo "  test        - Run basic tests"
	@echo "  lint        - Run code linting with flake8"
	@echo "  format      - Format code with black"
	@echo "  clean       - Clean up temporary files"
	@echo "  run         - Run the CLI application (use with ARGS='...')"
	@echo ""
	@echo "Examples:"
	@echo "  make install"
	@echo "  make test"
	@echo "  make run ARGS='portfolio --user johnsmith123'"

# Activate virtual environment for all commands
VENV = . venv/bin/activate &&

install:
	python3 -m venv venv
	$(VENV) pip install --upgrade pip
	$(VENV) pip install -r requirements.txt

test:
	$(VENV) python test_basic.py

lint:
	$(VENV) flake8 src/ --max-line-length=100
	$(VENV) flake8 etoro.py --max-line-length=100

format:
	$(VENV) black src/ etoro.py test_basic.py

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

run:
	$(VENV) python etoro.py $(ARGS)
