import requests
import json

SPARK_HOST = "localhost"

# Configuration
spark_master_url = f"http://{SPARK_HOST}:6066"
spark_job_endpoint = f"{spark_master_url}/v1/submissions/create"

# response = requests.get(spark_master_url+"/v1/submissions/status/driver-20240904072506-0000")
# print("Status for the job: ", "driver-20240904072506-0000")
# print(response.json())

# Path to your Spark application Python file on the master node
app_file = "/opt/spark-apps/end-to-end-example.py"  # Path to your script on the master

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
  "appArgs": [ app_file, "MONGO_HOST_PORT=mongo:27017", "MINIO_HOST_PORT=minio:9000", "MINIO_USER=admin12345", "MINIO_PASS=admin12345", "MINIO_BUCKET=sonem", "DATASET_PATH=datasets/ds1/clustering.csv", "RESULT_PATH=results/cl1/result.csv", "FEATURES=feature1,feature2", "K=3", "MAX_ITER=20" ]
}

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