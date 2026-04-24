import pandas as pd
import numpy as np
import random

# Sklearn libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# -------- LOAD DATASET --------
df = pd.read_csv("../data/ckd.csv")   # Read CKD dataset
df.columns = df.columns.str.strip()   # Remove extra spaces in column names


# -------- CLEAN TEXT DATA --------
# Remove spaces from string values
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)


# -------- SEPARATE TARGET --------
target = df['classification']   # Save target column separately


# -------- CONVERT TO NUMERIC --------
# Convert all columns to numeric except target
for col in df.columns:
    if col != 'classification':
        df[col] = pd.to_numeric(df[col], errors='coerce')  # Invalid → NaN


# -------- REMOVE EMPTY COLUMNS --------
df = df.dropna(axis=1, how='all')   # Drop columns with all missing values
df['classification'] = target       # Add target back


# -------- HANDLE MISSING VALUES --------
for col in df.columns:
    if col != 'classification':
        if df[col].dtype == 'float64' or df[col].dtype == 'int64':
            df[col] = df[col].fillna(df[col].mean())   # Fill numeric with mean
        else:
            df[col] = df[col].fillna(df[col].mode()[0])  # Fill categorical with mode


# -------- ENCODE TARGET --------
# Convert CKD → 1, Not CKD → 0
df['classification'] = df['classification'].apply(lambda x: 1 if x == 'ckd' else 0)


# -------- ENCODE CATEGORICAL DATA --------
le = LabelEncoder()  # Create encoder

for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = le.fit_transform(df[col])   # Convert text to numbers


# -------- SPLIT FEATURES & TARGET --------
X = df.drop('classification', axis=1)  # Input features
y = df['classification']               # Output (target)


# -------- NORMALIZATION --------
scaler = StandardScaler()
X = scaler.fit_transform(X)  # Scale data (important for ML)


# -------- TRAIN-TEST SPLIT --------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
# 80% training, 20% testing


# -------- CUCKOO SEARCH PARAMETERS --------
n_nests = 10                    # Number of solutions
n_features = X_train.shape[1]   # Total number of features
iterations = 10                 # Number of iterations


# -------- INITIALIZE NESTS --------
# Create random binary matrix (0 or 1)
# 1 = feature selected, 0 = not selected
nests = np.random.randint(2, size=(n_nests, n_features))


# -------- FITNESS FUNCTION --------
def fitness_function(solution):
    """
    Evaluate how good the selected features are
    """
    # Get selected feature indices
    selected = [i for i in range(n_features) if solution[i] == 1]

    # If no features selected → return 0 accuracy
    if len(selected) == 0:
        return 0

    # Train Random Forest model
    rf = RandomForestClassifier(n_estimators=100)
    rf.fit(X_train[:, selected], y_train)

    # Predict on test data
    y_pred = rf.predict(X_test[:, selected])

    # Return accuracy
    return accuracy_score(y_test, y_pred)


# -------- CUCKOO SEARCH LOOP --------
for _ in range(iterations):

    # Calculate fitness of all nests
    fitness = [fitness_function(n) for n in nests]

    # Select best nest (highest accuracy)
    best_nest = nests[np.argmax(fitness)]

    # Replace some nests with best solution
    for i in range(n_nests):
        if random.random() < 0.5:
            nests[i] = best_nest


# -------- BEST SOLUTION --------
best_solution = nests[np.argmax([fitness_function(n) for n in nests])]

# Get final selected features
selected = [i for i in range(n_features) if best_solution[i] == 1]

print("Selected Features (Cuckoo):", selected)


# -------- FINAL MODEL TRAINING --------
rf = RandomForestClassifier(n_estimators=100)

# Train model using selected features only
rf.fit(X_train[:, selected], y_train)

# Predict on test data
y_pred = rf.predict(X_test[:, selected])

# Print final accuracy
print("Cuckoo Accuracy:", accuracy_score(y_test, y_pred))