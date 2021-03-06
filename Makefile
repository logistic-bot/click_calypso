run:
	python main.py --user test --email test@example.com edit 353430d7-a043-4c2a-bd1c-57d816a65787 creator
style:
	@venv/bin/pylint -j 4 -f colorized *.py --exit-zero
	@venv/bin/flake8 --max-line-length=100 --max-doc-length=100 --show-source --statistics --exit-zero --jobs 4 --doctests --ignore W391 *.py
