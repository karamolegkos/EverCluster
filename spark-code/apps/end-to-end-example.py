# /opt/spark/bin/spark-submit --master spark://spark-master:7077 /opt/spark-apps/end-to-end-example.py MONGO_HOST_PORT=mongo:27017 MINIO_HOST_PORT=minio:9000 MINIO_USER=admin12345 MINIO_PASS=admin12345 MINIO_BUCKET=sonem DATASET_PATH=datasets/ds1/clustering.csv RESULT_PATH=results/cl1/result.csv FEATURES=feature1,feature2 K=3 MAX_ITER=20 MONGO_DATABASE=EverCluster CLUSTER_LABEL=cl1
# /opt/spark/bin/spark-submit /opt/spark-apps/end-to-end-example.py MONGO_HOST_PORT=mongo:27017 MINIO_HOST_PORT=minio:9000 MINIO_USER=admin12345 MINIO_PASS=admin12345 MINIO_BUCKET=sonem DATASET_PATH=datasets/ds1/clustering.csv RESULT_PATH=results/cl1/result.csv FEATURES=feature1,feature2 K=3 MAX_ITER=20 MONGO_DATABASE=EverCluster CLUSTER_LABEL=cl1
# apt install libffi-dev
# pip3 install --upgrade pip
# pip3 install pymongo
# pip3 install minio
# pip3 install --upgrade pandas
import sys

# Get the arguments
args = sys.argv[1:]

arguments = {}
for arg in args:
    key, value = arg.split("=")
    arguments[key] = value

# Parse the arguments
MONGO_HOST_PORT = arguments["MONGO_HOST_PORT"]
MINIO_HOST_PORT = arguments["MINIO_HOST_PORT"]
MINIO_USER = arguments["MINIO_USER"]
MINIO_PASS = arguments["MINIO_PASS"]
MINIO_BUCKET = arguments["MINIO_BUCKET"]
DATASET_PATH = arguments["DATASET_PATH"]
RESULT_PATH = arguments["RESULT_PATH"]
FEATURES = arguments["FEATURES"]
K = int(arguments["K"])
MAX_ITER = int(arguments["MAX_ITER"])
MONGO_DATABASE = arguments["MONGO_DATABASE"]
CLUSTER_LABEL = arguments["CLUSTER_LABEL"]

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pymongo import MongoClient
from minio import Minio
import pandas as pd
from io import BytesIO
import time

""" Minio Initializations """
minio_host = MINIO_HOST_PORT
client = Minio(
    minio_host,
    access_key=MINIO_USER,
    secret_key=MINIO_PASS,
    secure=False
)

response = client.get_object(MINIO_BUCKET, DATASET_PATH)

# Load the data into a Pandas DataFrame
df = pd.read_csv(BytesIO(response.data))

""" Spark Code """
# Initialize a Spark session
spark = SparkSession.builder \
    .appName("End to End Example")  \
    .master("spark://spark-master:7077")   \
    .getOrCreate()

# Create an RDD from the Pandas DataFrame
df = spark.createDataFrame(df)

# Print the DataFrame schema
df.printSchema()

# Print the first 5 rows
df.show(5)

# Clustering Example
feature_columns = FEATURES.split(",")
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
assembled_df = assembler.transform(df)

# Train a KMeans model
start_time = time.time()    # Start the timer
kmeans = KMeans().setK(K).setMaxIter(MAX_ITER).setSeed(1) # Seed for reproducibility
model = kmeans.fit(assembled_df)

# Make predictions
predictions = model.transform(assembled_df)
total_seconds = time.time() - start_time    # Calculate the time taken to cluster

# Evaluate clustering by computing Within Set Sum of Squared Errors
evaluator = ClusteringEvaluator()
silhouette = evaluator.evaluate(predictions)
print(f"Silhouette with squared euclidean distance = {silhouette}")

# Show the results (excluding the 'features' column)
# predictions.select('id', 'feature1', 'feature2', 'prediction').show()
columns_to_show = [col for col in predictions.columns if col != 'features']
predictions.select(columns_to_show).show()

# Removed the 'features' column from the predictions DataFrame
predictions = predictions.drop('features')

# Make predictions RDD back to Pandas DataFrame
predictions = predictions.toPandas()

# Print the first 5 rows
# predictions.show(5)

# Write the resulting DataFrame with predictions to a new CSV file in Minio
csv_bytes = predictions.to_csv().encode('utf-8')
csv_buffer = BytesIO(csv_bytes)

client.put_object(MINIO_BUCKET,
                RESULT_PATH,
                data=csv_buffer,
                length=len(csv_bytes),
                content_type='application/csv')

# Update MongoDB with the clustering results
mongoClient = MongoClient('mongodb://'+MONGO_HOST_PORT+'/')
db = mongoClient[MONGO_DATABASE]
collection = db['users']
# Update the user's clustering results with the time taken to cluster and the accuracy
# collection.update_one({"username": MINIO_BUCKET}, {"$set": {"clustering_results."+CLUSTER_LABEL: {"time_taken": total_seconds, "accuracy": silhouette}}})
collection.update_one({"username": MINIO_BUCKET}, {"$set": {"clustering_results."+CLUSTER_LABEL+".time_taken": total_seconds}})
collection.update_one({"username": MINIO_BUCKET}, {"$set": {"clustering_results."+CLUSTER_LABEL+".accuracy": silhouette}})

# Stop the Spark session
spark.stop()











