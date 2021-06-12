SHELL:=/usr/bin/env bash


.PHONY: lint_python
lint_python:
	poetry run mypy location_extractor tests
	poetry run flake8 location_extractor tests
	# TODO(skarzi): introduce `import-linter`
	# poetry run lint-imports


.PHONY: unit
unit:
	poetry run pytest --dead-fixtures --dup-fixtures
	poetry run pytest


.PHONY: lint_package
lint_package:
	poetry check
	poetry run pip check
	poetry run safety check --full-report


.PHONY: lint_complexity
lint_complexity:
	poetry run wily build location_extractor tests
	poetry run wily \
		--config=setup.cfg \
	diff \
		--revision=master \
	location_extractor tests


.PHONY: lint_complexity
lint_yaml:
	poetry run yamllint --format colored .


.PHONY: test
test: lint_python unit lint_package lint_yaml
