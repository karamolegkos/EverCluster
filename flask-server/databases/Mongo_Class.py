import os
from pymongo import MongoClient

class Mongo_Class:
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_DATABASE = os.getenv("MONGO_DATABASE", "EverCluster")

    def __init__(self):
        return
    
    # Check if a user exists in the database
    def user_exists(username, password):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        user = collection.find_one({"username": username, "password": password})

        mongo_client.close()

        return user is not None
    
    # Add a new user to the database
    def add_user(username, password):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        collection.insert_one({"username": username, "password": password, "datasets": {}, "clustering_results": {}})

        mongo_client.close()

        return
    
    # Add a new dataset to a user
    def add_dataset(user, file_metadata):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        collection.update_one({"username": user}, {"$set": {"datasets."+file_metadata["label"]: file_metadata}})

        mongo_client.close()

        return
    
    # Get all datasets from a user
    def get_datasets(user):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        datasets = collection.find_one({"username": user})["datasets"]

        mongo_client.close()

        return datasets
    
    # Get the filename of a dataset from a user
    def get_dataset_filename(user, label):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        filename = collection.find_one({"username": user})["datasets"][label]["filename"]

        mongo_client.close()

        return filename
    
    # Check if a dataset exists for a user
    def dataset_label_exists(user, label):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        dataset = collection.find_one({"username": user, "datasets."+label: {"$exists": True}})

        mongo_client.close()

        return dataset is not None
    
    # Delete a dataset from a user
    def delete_dataset(user, label):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        collection.update_one({"username": user}, {"$unset": {"datasets."+label: ""}})

        mongo_client.close()

        return
    
    # Update the download URL of a dataset's metadata
    def update_dataset_download_url(user, label, download_url):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        collection.update_one({"username": user}, {"$set": {"datasets."+label+".download_url": download_url}})

        mongo_client.close()

        return
    # Get the Clustering Results of a user
    def get_clustering_results(user):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        clustering_results = collection.find_one({"username": user})["clustering_results"]

        mongo_client.close()

        return clustering_results
    
    # Check if a Clustering Result exists for a user
    def clustering_results_label_exists(user, label):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        clustering_result = collection.find_one({"username": user, "clustering_results."+label: {"$exists": True}})

        mongo_client.close()

        return clustering_result is not None
    
    # Get the filename of a Clustering Result from a user
    def get_clustering_result_filename(user, label):

        return "result.csv"
    
    # Delete a Clustering Result from a user
    def delete_clustering_result(user, clustering_label):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        collection.update_one({"username": user}, {"$unset": {"clustering_results."+clustering_label: ""}})

        mongo_client.close()

        return
    
    # Add a new Clustering Result to a user
    def add_clustering_result(user, result_metadata):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        collection.update_one({"username": user}, {"$set": {"clustering_results."+result_metadata["clustering_label"]: result_metadata}})

        mongo_client.close()

        return
    
    def update_clustering_status(user, clustering_label, status):
        mongo_client = MongoClient("mongodb://"+Mongo_Class.MONGO_HOST+":"+str(Mongo_Class.MONGO_PORT)+"/")
        
        db = mongo_client[Mongo_Class.MONGO_DATABASE]
        collection = db["users"]

        collection.update_one({"username": user}, {"$set": {"clustering_results."+clustering_label+".STATUS": status}})

        mongo_client.close()

        return