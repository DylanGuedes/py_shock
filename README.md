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

