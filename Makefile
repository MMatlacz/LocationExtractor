SHELL:=/usr/bin/env bash


.PHONY: lint_python
lint_python:
	mypy location_extractor
	flake8 location_extractor tests
	# TODO(skarzi): introduce `import-linter`
	# lint-imports


.PHONY: unit
unit:
	pytest --dead-fixtures --dup-fixtures
	pytest


.PHONY: lint_package
lint_package:
	poetry check
	pip check
	safety check --full-report


.PHONY: lint_complexity
lint_complexity:
	wily build location_extractor tests
	wily --config=setup.cfg diff --revision=master location_extractor tests


.PHONY: test
test: lint_python unit lint_package
