import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("../data/ckd.csv")
df.columns = df.columns.str.strip()

# Clean text
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Separate target
target = df['classification']

# Convert to numeric
for col in df.columns:
    if col != 'classification':
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Drop empty columns
df = df.dropna(axis=1, how='all')
df['classification'] = target

# Fill missing values
for col in df.columns:
    if col != 'classification':
        if df[col].dtype == 'float64' or df[col].dtype == 'int64':
            df[col] = df[col].fillna(df[col].mean())
        else:
            df[col] = df[col].fillna(df[col].mode()[0])

# Encode target
df['classification'] = df['classification'].apply(lambda x: 1 if x == 'ckd' else 0)

# Encode categorical
le = LabelEncoder()
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = le.fit_transform(df[col])

# Split data
X = df.drop('classification', axis=1)
y = df['classification']

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Random Forest
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

print("Random Forest Accuracy:", accuracy_score(y_test, y_pred))