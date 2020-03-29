SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	flake8 location_extractor tests

.PHONY: unit
unit:
	pytest

.PHONY: package
package:
	poetry check
	# TODO: make sure it can be enabled
	# pip check
	safety check --bare --full-report

.PHONY: complexity
complexity:
	wily build location_extractor tests
	wily --config=setup.cfg diff --revision=master location_extractor tests

.PHONY: test
test: lint unit package
