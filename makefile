check: test
test:
	@echo testing project
	@python -m unittest discover tests

run:
	@python controller.py

build:
	python setup.py build

install: build
	@echo installing
	python setup.py install -O2 --record install.log

uninstall:
	@echo uninstalling
	-test -e install.log && cat install.log | xargs rm || true

clean:
	-rm -rf .radi.py.dat
	-rm -rf *.pyc
	-rm -rf libradi/*.pyc
	-rm -rf dao/*.pyc
	-rm -rf tests/*.pyc
	-rm -rf MANIFEST
	-rm -rf build dist
	-rm -f database.db*

.PHONY: check test run build install uninstall clean
