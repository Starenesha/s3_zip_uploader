install:
	poetry install

build:
	poetry build

package-install:
	python3 -m pip uninstall cli_uploader -y
	python3 -m pip install dist/*.whl

setup: install build package-install

lint:
	poetry run flake8 file_uploader

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=file_uploader

test-coverage:
	poetry run pytest --cov=file_uploader --cov-report xml