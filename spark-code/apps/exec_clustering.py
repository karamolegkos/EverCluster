from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pymongo import MongoClient
from minio import Minio
import pandas as pd
from io import BytesIO
# from pyspark.sql.functions import col
# apt install libffi-dev
# pip3 install pymongo
# pip3 install minio

""" Mongo Testing """
mongoClient = MongoClient('mongodb://mongo:27017/')
db = mongoClient['EverCluster']
if "new_users" in db.list_collection_names():
    db.new_users.drop()
collection = db['users']
# Create a new Collection named new_users with the same data
new_collection = db['new_users']
db.new_users.insert_many(db.users.find())
""" End of Mongo Testing """

""" Minio Testing """
minio_host = "minio:9000"
client = Minio(
    minio_host,
    access_key="admin12345",
    secret_key="admin12345",
    secure=False
)

response = client.get_object("sonem", "datasets/ds1/clustering.csv")

# Load the data into a Pandas DataFrame
df = pd.read_csv(BytesIO(response.data))

# df = pd.DataFrame()
csv_bytes = df.to_csv().encode('utf-8')
csv_buffer = BytesIO(csv_bytes)

client.put_object('sonem',
                       'mypath/test.csv',
                        data=csv_buffer,
                        length=len(csv_bytes),
                        content_type='application/csv')
""" End of Minio Testing """

# Initialize a Spark session
spark = SparkSession.builder \
    .appName("KMeans Clustering Example")  \
    .master("spark://spark-master:7077")   \
    .getOrCreate()

# Read a CSV file into a DataFrame
input_file = "/opt/spark-data/clustering.csv"
df = spark.read.csv(input_file, header=True, inferSchema=True)

# Assemble features into a feature vector
feature_columns = ['feature1', 'feature2']  # Replace with actual feature column names
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
assembled_df = assembler.transform(df)

# Train a KMeans model
kmeans = KMeans().setK(3).setSeed(1)  # k=3 clusters; set seed for reproducibility
model = kmeans.fit(assembled_df)

# Make predictions
predictions = model.transform(assembled_df)

# Evaluate clustering by computing Within Set Sum of Squared Errors
evaluator = ClusteringEvaluator()
silhouette = evaluator.evaluate(predictions)
print(f"Silhouette with squared euclidean distance = {silhouette}")

# Show the results (excluding the 'features' column)
predictions.select('id', 'feature1', 'feature2', 'prediction').show()

# Write the resulting DataFrame with predictions to a new CSV file
output_file = "/opt/spark-data/output_with_clusters.csv"
predictions.select('id', 'feature1', 'feature2', 'prediction') \
           .write.mode("overwrite") \
           .csv(output_file, header=True)

# Stop the Spark session
spark.stop()

# /opt/spark/bin/spark-submit --master spark://spark-master:7077 /opt/spark-apps/exec_clustering.py