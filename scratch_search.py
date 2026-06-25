import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

df_train = pd.read_csv("data/train_phase1.csv")
df_eval  = pd.read_csv("data/eval.csv")

X_train = df_train.drop(columns=["target"])
y_train = df_train["target"]
X_eval  = df_eval.drop(columns=["target"])
y_eval  = df_eval["target"]

from sklearn.model_selection import RandomizedSearchCV

param_dist = {
    'n_estimators': [100, 200, 300, 500],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap': [True, False]
}

rf = RandomForestClassifier(random_state=42)
search = RandomizedSearchCV(rf, param_distributions=param_dist, n_iter=20, cv=3, random_state=42, n_jobs=-1)
search.fit(X_train, y_train)

best_model = search.best_estimator_
preds = best_model.predict(X_eval)
acc = accuracy_score(y_eval, preds)

print(f"Best params: {search.best_params_}")
print(f"Accuracy: {acc}")
