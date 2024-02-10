# run single server container before compose the project
# to create default Postgres user credentials
install:
	docker build --no-cache -t hide-server .
	docker run -dit -p 80:80 -p 8080:8080 -p 5432:5432 --name hide-server hide-server
	docker exec hide-server sudo -u postgres psql -c "CREATE USER hide WITH PASSWORD 'he7w2rLY4Y8pFk2u';"
	docker exec hide-server sudo -u postgres psql -c "CREATE DATABASE hide;"
	docker stop hide-server
	docker-compose up -d
