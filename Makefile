run:
	python main.py
style:
	@pylint -j 4 -f colorized *.py --exit-zero
	@flake8 --max-line-length=80 --max-doc-length=80 --show-source --statistics --exit-zero --jobs 4 --doctests --ignore W391 *.py
