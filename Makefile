
setup:
	python setup.py install

test: clean setup
	python -m unittest discover test/

clean:
	pip uninstall -y cellini-odm
	rm -rf dist/
	rm -rf build/
	rm -rf cellini_odm.egg-info
	rm -rf .pytest_cache
	find -type d -name __pycache__ -exec rm -rf {} \; || true

coverage: clean setup
	pip install coverage
	python -m coverage run --source cellini/odm -m unittest discover test/
	python -m coverage report --format=markdown