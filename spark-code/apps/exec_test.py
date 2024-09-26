from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize a Spark session
spark = SparkSession.builder \
    .appName("Simple PySpark Script") \
    .getOrCreate()

# Read a CSV file into a DataFrame
input_file = "/opt/spark-data/input.csv"
df = spark.read.csv(input_file, header=True, inferSchema=True)

# Perform a simple transformation: filter rows where a column 'age' is greater than 30
filtered_df = df.filter(col("age") > 30)

# Select specific columns
selected_columns_df = filtered_df.select("name", "age")

# Show the resulting DataFrame
selected_columns_df.show()

# Write the resulting DataFrame to a new CSV file
output_file = "/opt/spark-data/output.csv"
selected_columns_df.write.mode("overwrite").csv(output_file, header=True)

# Stop the Spark session
spark.stop()

# spark-submit exec_test.py
# /opt/spark/bin/spark-submit --master spark://spark-master:7077 /opt/spark-apps/exec_test.py