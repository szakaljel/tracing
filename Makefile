linter:
	pylint service_a service_b service_c

start_service_a:
	. venv/bin/activate; ./service_a/run_server.sh

start_service_b:
	. venv/bin/activate; service_b/run_server.sh

start_service_c:
	. venv/bin/activate; service_c/run_worker.sh

start_env:
	docker-compose -f environment/docker-compose.yml up

stop_env:
	docker-compose -f environment/docker-compose.yml down

remove_venv:
	rm -rf venv

create_venv:
	virtualenv -p python3.8 venv
	. venv/bin/activate; pip install -r requirements.txt
