build:
	poetry build -f wheel

letsgo:
	poetry version patch
	poetry build -f wheel
	poetry publish

turnel:
	ngrok http 8002