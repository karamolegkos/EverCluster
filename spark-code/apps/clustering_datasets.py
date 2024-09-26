# /opt/spark/bin/spark-submit --master spark://spark-master:7077 /opt/spark-apps/clustering_datasets.py WORKERS=1 DATASET_NUMBER_DONE=0
from pyspark.sql import SparkSession
from pyspark.ml.clustering import KMeans, BisectingKMeans, GaussianMixture
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.functions import rand, randn, expr, min, max, col
import time, sys, random

# Get the WORKERS from the arguments
args = sys.argv[1:]
arguments = {}
for arg in args:
    key, value = arg.split("=")
    arguments[key] = value
WORKERS = int(arguments["WORKERS"])
DATASET_NUMBER_DONE = int(arguments["DATASET_NUMBER_DONE"])

# Workaround to execute the job many times and collect the results
if DATASET_NUMBER_DONE == 0:
    file_path = "/opt/spark-data/"+"workers-"+str(WORKERS)+".csv"
    f = open(file_path, "w")
    f.write("maxIteration,Clusters,Workers,ByteSize,RecordCount,FeaturesCount,ExecutionSpeed,Accuracy,Algorithm\n")
    f.close()

# Initialize Spark session
spark = SparkSession.builder.appName("Clustering Datasets Creator").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

def generate_dataset(num_rows, num_features):
    df = spark.range(0, num_rows)
    
    for i in range(num_features):
        # Choose a random distribution type
        distribution_type = random.choice([0, 1, 2])
        
        if distribution_type == 0:
            # Uniform distribution
            df = df.withColumn(f'feature_{i}', rand())
        elif distribution_type == 1:
            # Normal distribution
            df = df.withColumn(f'feature_{i}', randn())
        else:
            # Exponential distribution (by taking the log of a uniform distribution)
            df = df.withColumn(f'feature_{i}', -expr("log(rand())"))

        # Normalize the column to be between 0 and 1
        col_name = f'feature_{i}'
        min_val = df.agg(min(col(col_name))).first()[0]
        max_val = df.agg(max(col(col_name))).first()[0]
        df = df.withColumn(col_name, (col(col_name) - min_val) / (max_val - min_val))

    return df

def run_clustering_algorithms(dataset, k, maxIter):
    print("APPLICATION LOG: Dataset is being processed in kmeans, bisecting kmeans, and gaussian mixture algorithms")
    # dataset.show()
    results = []

    # Assemble features into a single column
    feature_columns = [col for col in dataset.columns if col != "id"]  # Assuming 'id' is not a feature
    assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
    dataset = assembler.transform(dataset)

    # KMeans v3
    kmeans = KMeans().setK(k).setMaxIter(maxIter).setFeaturesCol("features")
    start_time = time.time()
    kmeans_model = kmeans.fit(dataset)
    kmeans_time = time.time() - start_time
    kmeans_wssse = kmeans_model.summary.trainingCost
    results.append(('KMeans', kmeans_time, kmeans_wssse))

    # Bisecting KMeans
    bisecting_kmeans = BisectingKMeans().setK(k).setMaxIter(maxIter)
    start_time = time.time()
    bisecting_kmeans_model = bisecting_kmeans.fit(dataset)
    bisecting_kmeans_time = time.time() - start_time
    bisecting_kmeans_wssse = bisecting_kmeans_model.computeCost(dataset)
    results.append(('BisectingKMeans', bisecting_kmeans_time, bisecting_kmeans_wssse))

    # Gaussian Mixture
    gaussian_mixture = GaussianMixture().setK(k).setMaxIter(maxIter)
    start_time = time.time()
    gaussian_mixture_model = gaussian_mixture.fit(dataset)
    gaussian_mixture_time = time.time() - start_time
    gaussian_mixture_logLikelihood = gaussian_mixture_model.summary.logLikelihood
    results.append(('GaussianMixture', gaussian_mixture_time, gaussian_mixture_logLikelihood))

    return results

# loop for multiple datasets
print("APPLICATION LOG: Loop for multiple datasets and configurations (Synthetic Generation & Clustering)")
training_data = []

dataset_to_check = 1
# for num_rows in [4000, 1000, 500, 100, 25, 10]:
for num_rows in [10, 25, 100, 500, 1000, 4000]:
    # for num_features in [25, 10, 5, 3]:
    for num_features in [3, 5, 10, 25]:
        # Scip if the dataset has already been processed
        if dataset_to_check <= DATASET_NUMBER_DONE - 9:
            print("APPLICATION LOG: Datasets already processed. Skipping 9...")
            dataset_to_check += 9
            continue
        dataset = generate_dataset(num_rows, num_features)
        # for k in [5, 3, 2]:
        for k in [2, 3, 5]:
            # for maxIter in [50, 25, 10]:
            for maxIter in [10, 25, 50]:
                print(f"APPLICATION LOG: ---> Running clustering algorithms for dataset with {num_rows} rows, {num_features} features, {k} clusters, and {maxIter} maxIter (Workers: {WORKERS})")

                # Checking if this dataset has already been processed
                if dataset_to_check <= DATASET_NUMBER_DONE:
                    print("APPLICATION LOG: Dataset already processed. Skipping...")
                    dataset_to_check += 1
                    continue
                dataset_to_check += 1

                results = run_clustering_algorithms(dataset, k=k, maxIter=maxIter)
                byte_size = dataset.count() * len(dataset.columns) * 8  # Rough estimate
                record_count = dataset.count()
                for result in results:
                    file_path = "/opt/spark-data/"+"workers-"+str(WORKERS)+".csv"
                    f = open(file_path, "a")
                    f.write(f"{maxIter},{k},{WORKERS},{byte_size},{record_count},{num_features},{result[1]},{result[2]},{result[0]}\n")
                    f.close()
                # Increment the dataset number to avoid overwriting the results
                print(f"APPLICATION LOG: DATASETS DONE: {DATASET_NUMBER_DONE + 1}")
                DATASET_NUMBER_DONE += 1
print("APPLICATION LOG: End of Clustering (Synthetic Generation & Clustering)")