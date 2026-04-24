import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ---------------- FITNESS FUNCTION ----------------
def fitness_function(solution, X, y):
    # If no feature selected, return 0
    if np.sum(solution) == 0:
        return 0

    selected_features = np.where(solution == 1)[0]
    X_selected = X[:, selected_features]

    X_train, X_test, y_train, y_test = train_test_split(
        X_selected, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return accuracy_score(y_test, y_pred)


# ---------------- FIREFLY ALGORITHM ----------------
def firefly_algorithm(X, y, n_fireflies=10, max_iter=20, alpha=0.5, beta=1, gamma=1):
    n_features = X.shape[1]

    # Initialize fireflies (random binary solutions)
    fireflies = np.random.randint(2, size=(n_fireflies, n_features))
    fitness = np.array([fitness_function(f, X, y) for f in fireflies])

    for iteration in range(max_iter):
        for i in range(n_fireflies):
            for j in range(n_fireflies):
                if fitness[j] > fitness[i]:
                    # Distance
                    r = np.linalg.norm(fireflies[i] - fireflies[j])

                    # Move firefly i towards j
                    beta_eff = beta * np.exp(-gamma * r**2)

                    step = alpha * (np.random.rand(n_features) - 0.5)
                    new_solution = fireflies[i] + beta_eff * (fireflies[j] - fireflies[i]) + step

                    # Convert to binary (0/1)
                    new_solution = np.where(new_solution > 0.5, 1, 0)

                    new_fit = fitness_function(new_solution, X, y)

                    if new_fit > fitness[i]:
                        fireflies[i] = new_solution
                        fitness[i] = new_fit

        print(f"Iteration {iteration+1} Best Accuracy: {max(fitness)}")

    # Best solution
    best_index = np.argmax(fitness)
    best_solution = fireflies[best_index]
    best_features = np.where(best_solution == 1)[0]

    return best_features, max(fitness)


# ---------------- MAIN RUN ----------------
if __name__ == "__main__":
    # Example: Load your processed data from notebook
    import pandas as pd

    df = pd.read_csv("../data/ckd.csv")

    # Basic cleaning (same as your project)
    df.columns = df.columns.str.strip()
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    target = df['classification']

    for col in df.columns:
        if col != 'classification':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(axis=1, how='all')
    df['classification'] = target

    for col in df.columns:
        if col != 'classification':
            if df[col].dtype != 'object':
                df[col] = df[col].fillna(df[col].mean())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])

    df['classification'] = df['classification'].apply(lambda x: 1 if x == 'ckd' else 0)

    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = le.fit_transform(df[col])

    X = df.drop('classification', axis=1).values
    y = df['classification'].values

    # Run Firefly
    best_features, best_acc = firefly_algorithm(X, y)

    print("\nSelected Features Index:", best_features)
    print("Accuracy after Firefly:", best_acc)