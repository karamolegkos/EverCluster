import json, requests

SPARK_HOST = "localhost"

def submit_job(
        user, 
        algorithm, 
        dataset_label, 
        cluster_label, 
        cluster_amount, 
        max_iterations, 
        dataset_filename, 
        features,
        mongo_host,
        mongo_port,
        mongo_database,
        minio_host,
        minio_port,
        minio_user,
        minio_pass):
    
    # The Algorithms:
    algorithms = {
        "K-means": "end-to-end-example.py",
        "Gaussian mixture": "end-to-end-example.py",
        "Power iteration clustering (PIC)": "end-to-end-example.py",
        "Latent Dirichlet allocation (LDA)": "end-to-end-example.py",
        "Bisecting K-means": "end-to-end-example.py"
    }

    spark_master_url = f"http://{SPARK_HOST}:6066"
    spark_job_endpoint = f"{spark_master_url}/v1/submissions/create"

    # Path to your Spark application Python file on the master node
    # More Algorithms should exist here in the future 
    app_file = "/opt/spark-apps/"+algorithms[algorithm]  # Path on the master's script

    # Spark submission parameters
    data = {
        "appResource": "file://"+app_file,
        "sparkProperties": {
            "spark.master": f"spark://{SPARK_HOST}:7077",
            "spark.eventLog.enabled": "false",
            "spark.app.name": "Spark REST API - PI",
            "spark.submit.deployMode": "cluster",
            "spark.driver.supervise": "false"
        },
        "clientSparkVersion": "3.2.0",
        "mainClass": "org.apache.spark.deploy.SparkSubmit",
        "environmentVariables": {
            "SPARK_ENV_LOADED": "1"
        },
        "action": "CreateSubmissionRequest",
        "appArgs": [
            app_file, 
            "MONGO_HOST_PORT="+mongo_host+":"+str(mongo_port), 
            "MINIO_HOST_PORT="+minio_host+":"+str(minio_port),
            "MINIO_USER="+minio_user,  
            "MINIO_PASS="+minio_pass, 
            "MINIO_BUCKET="+user, 
            "DATASET_PATH=datasets/"+dataset_label+"/"+dataset_filename, 
            "RESULT_PATH=results/"+cluster_label+"/result.csv", 
            "FEATURES="+features, 
            "K="+str(cluster_amount), 
            "MAX_ITER="+str(max_iterations),
            "MONGO_DATABASE="+mongo_database,
            "CLUSTER_LABEL="+cluster_label
        ]
    }

    print(data)

    # Send the submission request
    headers = {'Content-Type': 'application/json'}
    response = requests.post(spark_job_endpoint, data=json.dumps(data), headers=headers)

    # Check the response
    if response.status_code == 200:
        print("Job submitted successfully.")
        print("Response JSON:", response.json())
    else:
        print("Failed to submit job.")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

# Example usage
submit_job(
    user="sonem",
    algorithm="K-means",
    dataset_label="ds1",
    cluster_label="c10",
    cluster_amount=3,
    max_iterations=10,
    dataset_filename="clustering.csv",
    features="feature1,feature2",
    mongo_host="mongo",
    mongo_port=27017,
    mongo_database="EverCluster",
    minio_host="minio",
    minio_port=9000,
    minio_user="admin12345",
    minio_pass="admin12345"
)