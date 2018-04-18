dev:
	./vulns.py --dev

demo:
	./vulns.py

lint:
	flake8 vulns.py

pdf:
	node_modules/.bin/decktape reveal slides.html 'Philipp_Hagemeister-5_Sicherheitsluecken_in_Deiner_Python-Anwendung.pdf' --no-sandbox -s 1920x1080


.PHONY: demo dev lint pdf
