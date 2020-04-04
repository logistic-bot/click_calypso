run:
	python main.py
style:
	@black *.py -l 100
	@pylint -j 4 -f colorized *.py --exit-zero
	@flake8 --max-line-length=100 --max-doc-length=100 --show-source --statistics --exit-zero --jobs 4 --doctests --ignore W391 *.py
