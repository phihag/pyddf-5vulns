dev:
	./vulns.py --dev

demo:
	./vulns.py

lint:
	flake8 vulns.py

.PHONY: demo dev lint
