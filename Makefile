check: test
test:
	@python -c "import tests"

run:
	@python controller.py


clean:
	rm -f *.pyc tests/*.pyc database.db*
