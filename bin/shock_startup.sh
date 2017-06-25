pip install {kafka-python,asyncio,websockets,pytest,findspark,typing}
$SPARK_HOME/bin/spark-class  org.apache.spark.deploy.master.Master -h master
# $SPARK_HOME/bin/spark-submit \
#  --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0 \
#  --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.1.0 \
#  /shock/shock.py
