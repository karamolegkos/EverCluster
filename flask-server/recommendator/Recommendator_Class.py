import joblib
import pandas as pd

class Recommendator_Class:
    # Get the Classifiers from the PKL files
    SPEED_CLASSIFIER = joblib.load("recommendator/speed_classifier.pkl")
    ACCURACY_CLASSIFIER = joblib.load("recommendator/accuracy_classifier.pkl")

    def __init__(self):
        return
    
    def recommend_algorithm_speed(clusters_amount, features, byte_size, lines_amount, maxIterations, wokrers):
        # Create the DataFrame
        new_data = pd.DataFrame({
            "maxIteration": [maxIterations],
            "Clusters": [clusters_amount],
            "Workers": [wokrers],
            "ByteSize": [byte_size],
            "RecordCount": [lines_amount],
            "FeaturesCount": [features]
        })

        # Predict the best algorithm for speed
        best_by_speed = Recommendator_Class.SPEED_CLASSIFIER.predict(new_data)
        print(f"Recommended Algorithm for Speed: {best_by_speed[0]}")

        if best_by_speed[0] == "KMeans":
            return "K-means"
        elif best_by_speed[0] == "GaussianMixture":
            return "Gaussian mixture"
        elif best_by_speed[0] == "BisectingKMeans":
            return "Bisecting K-Means"
    
    def recommend_algorithm_acc(clusters_amount, features, byte_size, lines_amount, maxIterations, wokrers):
        # Create the DataFrame
        new_data = pd.DataFrame({
            "maxIteration": [maxIterations],
            "Clusters": [clusters_amount],
            "Workers": [wokrers],
            "ByteSize": [byte_size],
            "RecordCount": [lines_amount],
            "FeaturesCount": [features]
        })

        # Predict the best algorithm for accuracy
        best_by_accuracy = Recommendator_Class.ACCURACY_CLASSIFIER.predict(new_data)
        print(f"Recommended Algorithm for Accuracy: {best_by_accuracy[0]}")

        if best_by_accuracy[0] == "KMeans":
            return "K-means"
        elif best_by_accuracy[0] == "GaussianMixture":
            return "Gaussian mixture"
        elif best_by_accuracy[0] == "BisectingKMeans":
            return "Bisecting K-Means"