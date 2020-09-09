build:
	poetry build -f wheel

letsgo:
	poetry version patch
	poetry build -f wheel
	poetry publish
