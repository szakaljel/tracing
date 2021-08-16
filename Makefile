linter:
	. venv/bin/activate; pylint common order delivery notification

start_order_service:
	. venv/bin/activate; order/run_server.sh

start_delivery_service:
	. venv/bin/activate; delivery/run_server.sh

start_notification_service:
	. venv/bin/activate; notification/run_worker.sh

start_env:
	docker-compose -f environment/docker-compose.yml up

stop_env:
	docker-compose -f environment/docker-compose.yml down

remove_venv:
	rm -rf venv

create_venv:
	virtualenv -p python3.8 venv
	. venv/bin/activate; pip install -r requirements.txt
