# Shock - InterSCity's Data Pipeline

## Usage

1. Register functions in topic `new_pipeline_instruction` with the following syntax:
```sh
$ fileWithTheFunction;Function
```
i.e:
```sh
$ datapipeline;countWords
```
2. Generate information in `interscity` topic (via Kafka, for instance)

## Using the sp-collector

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
$ sphinx-build docs/ docs_mount/
```
