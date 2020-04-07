run:
	python main.py --user test --email test@example.com repl
style:
	@venv/bin/pylint -j 4 -f colorized *.py --exit-zero
	@venv/bin/flake8 --max-line-length=100 --max-doc-length=100 --show-source --statistics --exit-zero --jobs 4 --doctests --ignore W391 *.py
