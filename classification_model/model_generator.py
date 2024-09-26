# pip install scikit-learn
# pip install pandas
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Load the datasets
df_training_1 = pd.read_csv("./workers-1.csv")
df_training_2 = pd.read_csv("./workers-2.csv")
df_training_3 = pd.read_csv("./workers-3.csv")
df_training_4 = pd.read_csv("./workers-4.csv")
df_training_5 = pd.read_csv("./workers-5.csv")

# Concatenate the datasets
df_training = pd.concat([df_training_1, df_training_2, df_training_3, df_training_4, df_training_5])
# print(df_training)

# Create empty Dataset to store the values of the best algorithm per three rows
df_clean_training = pd.DataFrame(columns=["maxIteration", "Clusters", "Workers", "ByteSize", "RecordCount", "FeaturesCount"])
# Create empty Dataset to store the best algorithm per three rows
df_best_execSpeed = pd.DataFrame(columns=["BestBySpeed"])
df_best_execAccuracy = pd.DataFrame(columns=["BestByAccuracy"])

# Loop the df_training per three rows and print the algorithm feature
for i in range(0, len(df_training), 3):
    alg_1 = df_training.iloc[i]["Algorithm"]
    alg_2 = df_training.iloc[i+1]["Algorithm"]
    alg_3 = df_training.iloc[i+2]["Algorithm"]

    # Find the algorithm with the best speed
    if df_training.iloc[i]["ExecutionSpeed"] < df_training.iloc[i+1]["ExecutionSpeed"] and df_training.iloc[i]["ExecutionSpeed"] < df_training.iloc[i+2]["ExecutionSpeed"]:
        best_speed = alg_1
    elif df_training.iloc[i+1]["ExecutionSpeed"] < df_training.iloc[i]["ExecutionSpeed"] and df_training.iloc[i+1]["ExecutionSpeed"] < df_training.iloc[i+2]["ExecutionSpeed"]:
        best_speed = alg_2
    else:
        best_speed = alg_3

    # Find the algorithm with the best accuracy
    if df_training.iloc[i]["Accuracy"] < df_training.iloc[i+1]["Accuracy"] and df_training.iloc[i]["Accuracy"] < df_training.iloc[i+2]["Accuracy"]:
        best_accuracy = alg_1
    elif df_training.iloc[i+1]["Accuracy"] < df_training.iloc[i]["Accuracy"] and df_training.iloc[i+1]["Accuracy"] < df_training.iloc[i+2]["Accuracy"]:
        best_accuracy = alg_2
    else:
        best_accuracy = alg_3

    # Append the best algorithm to the df_best_execSpeed and df_best_execAccuracy
    # df_best_execSpeed = df_best_execSpeed.append({"BestBySpeed": best_speed}, ignore_index=True)
    df_best_execSpeed.loc[len(df_best_execSpeed.index)] = [best_speed]
    # df_best_execAccuracy = df_best_execAccuracy.append({"BestByAccuracy": best_accuracy}, ignore_index=True)
    df_best_execAccuracy.loc[len(df_best_execAccuracy.index)] = [best_accuracy]

    # Append the features of the three algorithms to the df_clean_training (They are the same for the three algorithms)
    # df_clean_training = df_clean_training.append(df_training.iloc[i][["maxIteration", "Clusters", "Workers", "ByteSize", "RecordCount", "FeaturesCount"]], ignore_index=True)
    df_clean_training.loc[len(df_clean_training.index)] = df_training.iloc[i][["maxIteration", "Clusters", "Workers", "ByteSize", "RecordCount", "FeaturesCount"]]
        


# Prepare features and labels
X = df_clean_training[["maxIteration", "Clusters", "Workers", "ByteSize", "RecordCount", "FeaturesCount"]]
y_speed = df_best_execSpeed["BestBySpeed"]
y_accuracy = df_best_execAccuracy["BestByAccuracy"]


# Split the data into training and testing sets
X_train, X_test, y_speed_train, y_speed_test = train_test_split(X, y_speed, test_size=0.2, random_state=42)
_, _, y_accuracy_train, y_accuracy_test = train_test_split(X, y_accuracy, test_size=0.2, random_state=42)   # The same random state so the split is the same

# Train the Speed Classifier
speed_classifier = RandomForestClassifier()
speed_classifier.fit(X_train, y_speed_train)

# Train the Accuracy Classifier
accuracy_classifier = RandomForestClassifier()
accuracy_classifier.fit(X_train, y_accuracy_train)

# Evaluate Speed Classifier
y_speed_pred = speed_classifier.predict(X_test)
speed_accuracy = accuracy_score(y_speed_test, y_speed_pred)
print(f"Speed Classifier Accuracy: {speed_accuracy:.2f}")

# Evaluate Accuracy Classifier
y_accuracy_pred = accuracy_classifier.predict(X_test)
accuracy_accuracy = accuracy_score(y_accuracy_test, y_accuracy_pred)
print(f"Accuracy Classifier Accuracy: {accuracy_accuracy:.2f}")

""" Saving of the Models """
# Save the models
joblib.dump(speed_classifier, "speed_classifier.pkl")        # Save the model to PKL file (serialized Python object)
joblib.dump(accuracy_classifier, "accuracy_classifier.pkl")  # Save the model to PKL file (serialized Python object)

# To load the models
# speed_classifier = joblib.load("speed_classifier.pkl")
# accuracy_classifier = joblib.load("accuracy_classifier.pkl")

"""
# Example new data
new_data = pd.DataFrame({
    "maxIteration": [25],
    "Clusters": [3],
    "Workers": [6],
    "ByteSize": [5000],
    "RecordCount": [1000],
    "FeaturesCount": [8]
})

# Predict the best algorithm for speed
best_by_speed = speed_classifier.predict(new_data)
print(f"Recommended Algorithm for Speed: {best_by_speed[0]}")

# Predict the best algorithm for accuracy
best_by_accuracy = accuracy_classifier.predict(new_data)
print(f"Recommended Algorithm for Accuracy: {best_by_accuracy[0]}")
"""