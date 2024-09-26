# Import Libraries
from datetime import datetime
import os, json
from flask import Flask, request, session, redirect, render_template, url_for
from werkzeug.utils import secure_filename
from databases.Mongo_Class import Mongo_Class as Mongo
from databases.MinIO_Class import MinIO_Class as MinIO
from spark_handler.Spark_Handler_Class import Spark_Handler_Class as SparkHandler
from file_reader.File_Reader_Class import File_Reader_Class as FileReader
from recommendator.Recommendator_Class import Recommendator_Class as Recommendator
import threading

""" Environment Variables """
# Flask app Host and Port
APP_HOST = os.getenv("APP_HOST", "localhost")
APP_PORT = int(os.getenv("APP_PORT", 5000))

""" Global variables """
# The name of the flask app
app = Flask(__name__)
# app.secret_key = 'a_random_key'  # Needed to use sessions
app.secret_key = 'EverClusterKey'  # Needed to use sessions

""" User Endpoints """
# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    # Check if the user is already logged in
    if "user" in session:
        return redirect(url_for("home"))

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check the credentials
        if Mongo.user_exists(username, password):
            # Add the user to the session
            session["user"] = username
            return redirect(url_for('home'))
        else:
            error = 'Invalid Credentials'
    return render_template('login.html', error=error)

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if the user is already logged in
    if "user" in session:
        return redirect(url_for("home"))
    
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']

        # Test if the passwords match
        if password != password2:
            error = 'Passwords do not match'
            return render_template('register.html', error=error)

        # Check the credentials
        if not Mongo.user_exists(username, password):
            # Add the user to the session and add the user to the database
            Mongo.add_user(username, password)
            session["user"] = username

            return redirect(url_for('home'))
        else:
            error = 'User already exists'
    return render_template('register.html', error=error)

# Home Page
@app.route("/home", methods=["GET"])
def home():
    # Check if the user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    
    # Get the Spark's Cluster Status
    master_online, worker_amount = SparkHandler.get_cluster_status()

    return render_template("home.html", master_online=master_online, worker_amount=worker_amount, user=session["user"])

# Logout Page
@app.route("/logout", methods=["GET"])
def logout():
    # Check if the user is logged in
    if "user" in session:
        session.pop("user")
    return redirect(url_for("login"))

""" Application Endpoints """
# Upload Dataset Page
@app.route("/upload", methods=["GET", "POST"])
def upload():
    error = None
    # Check if the user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    
    user = session["user"]

    # Get the Spark's Cluster Status
    master_online, worker_amount = SparkHandler.get_cluster_status()

    # Get all the Datasets of the user and display them
    datasets = Mongo.get_datasets(user)

    if "_method" in request.form:
        if request.method == "POST" and request.form["_method"] == "DELETE":
            # Get the label of the dataset to delete
            label = request.form["label"]
            print("Label: ", label)

            # Check if the label exists
            if not Mongo.dataset_label_exists(user, label):
                error = "Label does not exist"
                return render_template("upload.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

            # Get the filename of the dataset
            filename = Mongo.get_dataset_filename(user, label)

            # Delete the dataset from the databases
            MinIO.delete_dataset_object(filename, user, label)
            Mongo.delete_dataset(user, label)

            return redirect(url_for("upload"))

    if request.method == "POST":
        # Check if the label is valid
        label = request.form["dataset_label"]
        if label == "":
            error = "No label provided"
            return render_template("upload.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Check if the label has spaces
        if " " in label:
            error = "Label cannot have spaces"
            return render_template("upload.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)
        
        # Check if the label has special characters
        if not label.isalnum():
            error = "Label can only have letters and numbers"
            return render_template("upload.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)
        
        # Check if the label starts with a number
        if label[0].isdigit():
            error = "Label cannot start with a number"
            return render_template("upload.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Check if label already exists in the database
        if Mongo.dataset_label_exists(user, label):
            error = "Label already exists"
            return render_template("upload.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)
        
        # Check if the post request has the file part
        if "dataset_file" not in request.files:
            error = "No file part in the request"
            return render_template("upload.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        file = request.files["dataset_file"]
        
        # If the user does not select a file, the browser submits an empty part without a filename
        if file.filename == "":
            error = "No file selected"
            return render_template("upload.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)
        
        # Check if the file is valid
        valid, error = FileReader.check_file_validity(file)
        if not valid:
            return render_template("upload.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Get more information about the file
        filename = secure_filename(file.filename)
        size = os.fstat(file.fileno()).st_size

        # Get current Date and Time
        date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        file_metadata = FileReader.get_file_metadata(file)
        file_metadata["filename"] = filename
        file_metadata["size"] = size
        file_metadata["label"] = label
        file_metadata["date"] = date

        # Add the file to the databases
        Mongo.add_dataset(user, file_metadata)
        download_url = MinIO.upload_dataset_object(filename, file, size, user, label)

        # Update the download url in the database
        Mongo.update_dataset_download_url(user, label, download_url)

        return redirect(url_for("upload"))
    
    # print("Datasets: ", datasets)

    return render_template("upload.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

# Clustering Page
@app.route("/clustering", methods=["GET", "POST"])
def clustering():
    error = None
    # Check if the user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    
    user = session["user"]

    # Get the Spark's Cluster Status
    master_online, worker_amount = SparkHandler.get_cluster_status()

    # Get all the Datasets of the user and display them
    datasets = Mongo.get_datasets(user)

    if request.method == "POST":
        # Get the label of the dataset to cluster
        print("Request Form: ", request.form)
        dataset_label = request.form["datasets"]

        # Check if the label exists
        if not Mongo.dataset_label_exists(user, dataset_label):
            error = "Dataset Label does not exist"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Get the number of clusters
        clusters = request.form["clusters"]
        if clusters == '0':
            error = "No number of clusters provided"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Get the algorithm
        algorithm = request.form["algorithm"]
        if algorithm == "":
            error = "No algorithm provided"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Get the features
        features_str = request.form["headers"] # '["feature1","feature2"]' -> ["feature1","feature2"]
        features = features_str.replace('"', "").replace("[", "").replace("]", "").split(",")
        if features == []:
            error = "No features provided"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Check that features are two or more
        if len(features) < 2:
            error = "At least two features are required"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Get the output label
        cluster_label = request.form["cluster_label"]
        if cluster_label == "":
            error = "No clustering label provided"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Check if the label has spaces
        if " " in cluster_label:
            error = "Clustering Label cannot have spaces"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)
        
        # Check if the label has special characters
        if not cluster_label.isalnum():
            error = "Clustering Label can only have letters and numbers"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)
        
        # Check if the label starts with a number
        if cluster_label[0].isdigit():
            error = "Clustering Label cannot start with a number"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Check if the output label already exists
        if Mongo.clustering_results_label_exists(user, cluster_label):
            error = "Clustering label already exists"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)
    
        # Get the maxIterations
        maxIterations = request.form["maxIteration"]
        if maxIterations == "0":
            error = "No maxIterations provided"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        # Check that the clusters are not more than the rows of the dataset
        rows_amount = int(datasets[dataset_label]["lines"])
        if int(clusters) > rows_amount:
            error = "Clusters amount cannot be more than the rows of the dataset"
            return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

        print("Features: ", features)
        print("Algorithm: ", algorithm)
        print("Clusters: ", clusters)
        print("Cluster Label: ", cluster_label)
        print("Dataset Label: ", dataset_label)
        print("maxIterations: ", maxIterations)

        dataset = datasets[dataset_label]
        # print("Dataset: ", dataset)
        dataset["features"] = features
        cluster_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Get the Recommended Algorithm
        recommendation_speed = Recommendator.recommend_algorithm_speed(int(clusters), len(features), int(dataset["size"]), int(dataset["lines"]), int(maxIterations), int(worker_amount))
        recommendation_acc = Recommendator.recommend_algorithm_acc(int(clusters), len(features), int(dataset["size"]), int(dataset["lines"]), int(maxIterations), int(worker_amount))

        # Redirect to the recommendation page and pass the parameters
        return render_template("recommendation.html", user=user, master_online=master_online, worker_amount=worker_amount, clusters=clusters, algorithm=algorithm, cluster_label=cluster_label, dataset=dataset, recommendation_speed=recommendation_speed, recommendation_acc=recommendation_acc, cluster_date=cluster_date, maxIterations=maxIterations)

    return render_template("clustering.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, datasets=datasets)

# Recommendation URI
@app.route("/execute", methods=["POST"])
def execute():
    error = None
    # Check if the user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    
    user = session["user"]
    algorithm = request.form["algorithm"]
    dataset_label = request.form["dataset_label"]
    cluster_label = request.form["cluster_label"]
    clusters_amount = request.form["clusters_amount"]
    max_iterations = request.form["max_iterations"]
    dataset_filename = request.form["dataset_filename"]
    features = request.form["features"]
    cluster_date = request.form["cluster_date"]
    dataset_headers = request.form["dataset_headers"]

    # Fix the features string
    features = features.replace("'", '"')
    features = json.loads(features)
    features = ','.join(map(str, features))

    dataset_headers = dataset_headers.replace("'", '"')
    dataset_headers = json.loads(dataset_headers) 

    # Create a Mongo Record for the Clustering Result 
    result_metadata = {
        "algorithm": algorithm,
        "dataset_label": dataset_label,
        "clustering_label": cluster_label,
        "clusters_amount": clusters_amount,
        "max_iterations": max_iterations,
        "headers": dataset_headers,
        "features": features.split(","),
        "date": cluster_date,
        "STATUS": "RUNNING",
        "download_url" : "http://localhost:"+str(MinIO.MINIO_PORT)+"/"+user+"/results/" + cluster_label + "/" + "result.csv"
    }

    Mongo.add_clustering_result(user, result_metadata)

    # Use the Spark Handler to submit the job
    submissionId = SparkHandler.submit_job(
        user, 
        algorithm, 
        dataset_label, 
        cluster_label, 
        clusters_amount, 
        max_iterations, 
        dataset_filename, 
        features,
        Mongo.MONGO_HOST,
        Mongo.MONGO_PORT,
        Mongo.MONGO_DATABASE,
        MinIO.MINIO_HOST,
        MinIO.MINIO_PORT,
        MinIO.MINIO_USER,
        MinIO.MINIO_PASS
    )

    # Start Collecting the Job Status until it is Finished or Failed in another thread
    new_thread = threading.Thread(target=SparkHandler.listen_until_job_is_done, args=(user, cluster_label, submissionId))
    new_thread.start()

    return redirect(url_for("clustering_results"))

# View Clustering Results Page
@app.route("/clustering_results", methods=["GET", "POST"])
def clustering_results():
    error = None
    # Check if the user is logged in
    if "user" not in session:
        return redirect(url_for("login"))
    
    user = session["user"]

    # Get the Spark's Cluster Status
    master_online, worker_amount = SparkHandler.get_cluster_status()

    # Get all the Clustering Results of the user and display them
    clustering_results = Mongo.get_clustering_results(user)

    if "_method" in request.form:
        if request.method == "POST" and request.form["_method"] == "DELETE":
            # Get the label of the clustering result to delete
            label = request.form["label"]

            # Check if the label exists
            if not Mongo.clustering_results_label_exists(user, label):
                error = "Label does not exist"
                return render_template("clustering_results.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, results=clustering_results)

            # Get the filename of the clustering result
            filename = Mongo.get_clustering_result_filename(user, label)

            # Delete the clustering result from the databases
            MinIO.delete_clustering_result_object(filename, user, label)
            Mongo.delete_clustering_result(user, label)

            return redirect(url_for("clustering_results"))

    return render_template("clustering_results.html", error=error, user=user, master_online=master_online, worker_amount=worker_amount, results=clustering_results)

""" Main """
# Main code
if __name__ == "__main__":
    app.run(APP_HOST, APP_PORT, True)