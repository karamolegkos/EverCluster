import os, json
import requests
from time import sleep
from databases.Mongo_Class import Mongo_Class as Mongo

class Spark_Handler_Class:
    SPARK_HOST = os.getenv("SPARK_HOST", "localhost")
    SPARK_PORT = os.getenv("SPARK_PORT", 6066)

    def __init__(self):
        return
    
    def get_cluster_status():
        try:
            response = requests.get("http://"+Spark_Handler_Class.SPARK_HOST+":8080")
            page_text = response.text

            found_master = False
            for line in page_text.split("\n"):
                if "<li><strong>Status:</strong> ALIVE</li>" in line:
                    found_master = True

            if not found_master:
                return False, 0
            
            alive_workers = 0
            for line in page_text.split("\n"):
                if "<td>ALIVE</td>" in line:
                    alive_workers += 1
                
            return True, alive_workers
        except:
            return False, 0
        
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
            "K-means": "k-means.py",
            "Gaussian mixture": "gaussian-mixture.py",
            "Bisecting K-Means": "bk-means.py"
        }

        spark_master_url = f"http://{Spark_Handler_Class.SPARK_HOST}:6066"
        spark_job_endpoint = f"{spark_master_url}/v1/submissions/create"

        if algorithm not in algorithms:
            print("Algorithm not found. Algorithm is: "+algorithm)
        # Path to your Spark application Python file on the master node
        # More Algorithms should exist here in the future 
        app_file = "/opt/spark-apps/"+algorithms[algorithm]  # Path on the master's script

        # Spark submission parameters
        data = {
            "appResource": "file://"+app_file,
            "sparkProperties": {
                "spark.master": f"spark://{Spark_Handler_Class.SPARK_HOST}:7077",
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

        return response.json()["submissionId"]

    def get_job_status(job_id):
        spark_master_url = f"http://{Spark_Handler_Class.SPARK_HOST}:6066"
        spark_job_endpoint = f"{spark_master_url}/v1/submissions/status/{job_id}"
        response = requests.get(spark_job_endpoint)

        # Return the Status of the Job
        driver = response.json()["driverState"]
        return driver   # Can be "SUBMITTED", "RUNNING", "FINISHED", "FAILED", "UNKNOWN"
    
    def listen_until_job_is_done(user, clustering_label, job_id):
        print("Listening for job to finish...:"+ job_id)
        while True:
            status = Spark_Handler_Class.get_job_status(job_id)
            if status == "FINISHED" or status == "FAILED":
                break
            sleep(1)

        print("Job "+ job_id +" is done with Status: "+status)
        # If the job is finished, update the user's clustering results
        Mongo.update_clustering_status(user, clustering_label, status)
        return status

