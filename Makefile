# Directories
SRC_DIR = .
HELPERS_DIR = helpers

# Tools
BLACK = black
FLAKE8 = flake8

# Targets
.PHONY: all clean format lint test run install-dev

clean:
	rm -rf __pycache__ *.pyc

format:
	$(BLACK) $(SRC_DIR) $(HELPERS_DIR)

lint:
	$(FLAKE8) $(SRC_DIR) $(HELPERS_DIR)

test:
	pytest

install-dev:
	pip install black flake8 pytest
