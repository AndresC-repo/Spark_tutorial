build:
	docker-compose build

build-nc:
	docker-compose build --no-cache

build-progress:
	docker-compose build --no-cache --progress=plain

down:
	docker-compose down --volumes --remove-orphans

run:
	make down && docker-compose up

run-scaled:
	make down && docker-compose up --scale spark-worker=3

run-d:
	make down && docker-compose up -d

stop:
	docker-compose stop

submit:
	docker exec da-spark-master spark-submit \
	--master spark://spark-master:7077 \
	--deploy-mode client \
	--conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:/opt/spark/conf/log4j.properties" \
	--conf "spark.executor.extraJavaOptions=-Dlog4j.configuration=file:/opt/spark/conf/log4j.properties" \
	./apps/$(app)

shell:
	docker exec -it da-spark-master bash

submit-da-book:
	make submit app=data_analysis_book/$(app)

rm-results:
	rm -r book_data/results/*