restart:
	- docker compose --file docker-compose.yml --project-name api-tg stop
	git checkout master
	git pull origin master
	docker compose --file docker-compose.yml --project-name api_tg up -d --build
	echo CHECK container status