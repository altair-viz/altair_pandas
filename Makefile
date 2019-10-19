all: install

install:
	python setup.py install

test :
	black .
	flake8 altair_pandas
	python -m pytest --pyargs --doctest-modules altair_pandas

test-coverage:
	python -m pytest --pyargs --doctest-modules --cov=altair_pandas --cov-report term altair_pandas

test-coverage-html:
	python -m pytest --pyargs --doctest-modules --cov=altair_pandas --cov-report html altair_pandas
