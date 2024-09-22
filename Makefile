create_env:
	python -m venv .venv

# activate_env:
# 	source .venv/bin/activate.fish

# deactivate_env:
# 	deactivate

install_requirements:
	pip install -r requirements.txt

generate_requirements:
	pip freeze > requirements.txt

# python ./manage.py reset_db
run_migrations:
	python manage.py makemigrations && python manage.py migrate

run_server:
	docker-compose up redis -d && python manage.py runserver

run_tests:
	python manage.py test

enter_redis:
	docker-compose exec redis redis-cli -a pass -n 1

lint:
	python -m black .
