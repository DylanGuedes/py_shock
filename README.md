# Shock - InterSCity's Data Pipeline

## Running Shock

1. Install pip packages
```
$ pip install {typing,kafka-python,pytest,asyncio,websockets,findspark}
```

2. Run the bin with the correct packages
```
./bin/spark-submit \
--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0 \
--packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.1.0 \
shock.py
```

Or, in Docker container:
```
docker exec dataprocessor_master_1 -it ./bin/spark-submit \
--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0 \
--packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.1.0 \
/shock/shock.py
```


## Usage

1. Register functions in topic `new_pipeline_instruction` with the following syntax:
```sh
$ stage;args
```
i.e:
```sh
$ ingestion;{"shock_action": "kafkaIngestion"}
```
2. Generate information in `interscity` topic (via Kafka, for instance)

## Using the sp-collector

## Testing
```sh
$ pytest .
```

Or, via Docker container
```sh
$ docker exec -it dataprocessor_master_1 pytest /shock/.
```

1. Run pyspark:
```
$ ./bin/pyspark --conf "spark.mongodb.input.uri=mongodb://127.0.0.1/sp.weather" --conf "spark.mongodb.input.partitioner=MongoShardedPartitioner" --conf "spark.mongodb.output.uri=mongodb://127.0.0.1/sp.weather" --packages org.mongodb.spark:mongo-spark-connector_2.11:2.0.0
```

2. Read from mongo:
```python
>>> df = spark.read.format("com.mongodb.spark.sql.DefaultSource").load()
```

3. Use it!:
```python
>>> df.show() # show tables
...
...
...
>>> df.select("temperature").show() # show only column temperatures
...
...
...
>>> df.select("temperature").describe().show() # show temperature mean, stddev, etc
...
...
...
```

## Running the docs

1. Run
```
$ sphinx-autobuild docs/ docs_mount/
```
