build:
	poetry build -f wheel

patch:
	poetry version patch

update:
	poetry update

letsgo: update format patch publish

format:
	pre-commit run --all-files

publish: format build
	poetry publish

turnel:
	ngrok http 8002