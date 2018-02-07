dev:
	while true; do ./vulns.py & vulns_pid=$$!; inotifywait -e close_write vulns.py ; kill "$${vulns_pid}"; done


demo:
	./vulns.py

lint:
	flake8 vulns.py

.PHONY: demo dev lint
