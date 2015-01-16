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

dist: clean
	-mkdir -p dist
	-cp -r bottle.py dist
	-cp -r config.py dist/config.def.py
	-cp -r controller.py dist
	-cp -r dao dist
	-cp -r dict dist
	-cp -r libradi dist
	-cp -r makefile dist
	-cp -r netem.py dist
	-cp -r radi.py dist
	-cp -r readme.md dist
	-cp -r schema.sql dist/schema.def.sql
	-cp -r static dist
	-cp -r views dist
	@echo "Please copy config.def.py to config.py and schema.def.sql to schema.sql before running." >> dist/readme.md

clean:
	-rm -rf .radi.py.dat
	-rm -rf *.pyc
	-rm -rf libradi/*.pyc
	-rm -rf dao/*.pyc
	-rm -rf tests/*.pyc
	-rm -rf MANIFEST
	-rm -rf build dist
	-rm -f database.db*
	-rm -rf dist

.PHONY: check test run build install uninstall dist clean
