install:
	docker build --no-cache -t hide-server .
	docker-compose up -d
	docker exec hide-server sudo -u postgres psql -c "CREATE USER hide WITH PASSWORD 'he7w2rLY4Y8pFk2u';"
	docker exec hide-server sudo -u postgres psql -c "CREATE DATABASE hide;"
