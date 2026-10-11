
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)



BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


csv_files = sorted(DATA_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in {DATA_DIR}"
    )

if len(csv_files) > 1:
    print("CSV files found:")
    for file in csv_files:
        print(" -", file.name)
    raise ValueError(
        "Multiple CSV files found. Select the correct "
        "processed dataset explicitly."
    )

data = pd.read_csv(csv_files[0])
data.columns = data.columns.str.strip()

print("\nDataset:", csv_files[0].name)
print("Dataset shape:", data.shape)



possible_labels = ["Label", "label", "Class", "class", "target"]

target_col = next(
    (col for col in possible_labels if col in data.columns),
    None
)

if target_col is None:
    raise ValueError(
        "Target column not found. Available columns: "
        + str(data.columns.tolist())
    )

data = data.dropna(subset=[target_col]).copy()

y = data[target_col].astype(str).str.strip()


X = data.drop(columns=[target_col])


X = X.select_dtypes(include=["number"]).copy()

if X.empty:
    raise ValueError("No numeric feature columns found.")


X = X.replace([float("inf"), float("-inf")], float("nan"))


X = X.dropna(axis=1, how="all")


feature_names = X.columns.tolist()

if not feature_names:
    raise ValueError("No usable numeric features remain.")



X_temp, X_test, y_temp, y_test = train_test_split(
    X,
    y,
    test_size=0.15,
    random_state=42,
    stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp,
    y_temp,
    test_size=0.1764706,
    random_state=42,
    stratify=y_temp
)

print("\nData split:")
print("Training:", len(X_train))
print("Validation:", len(X_val))
print("Testing:", len(X_test))



medians = X_train.median().fillna(0)

X_train = X_train.fillna(medians)
X_val = X_val.fillna(medians)
X_test = X_test.fillna(medians)



model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

print("\nTraining Random Forest...")
model.fit(X_train, y_train)

print("Training completed!")


y_val_pred = model.predict(X_val)

print("\n========== VALIDATION RESULTS ==========")
print("Accuracy:", round(accuracy_score(y_val, y_val_pred), 4))

print("\nValidation classification report:")
print(
    classification_report(
        y_val,
        y_val_pred,
        zero_division=0
    )
)


y_test_pred = model.predict(X_test)

print("\n========== TEST RESULTS ==========")
print("Accuracy:", round(accuracy_score(y_test, y_test_pred), 4))
print("Precision (weighted):", round(
    precision_score(y_test, y_test_pred,
                    average="weighted", zero_division=0), 4
))
print("Recall (weighted):", round(
    recall_score(y_test, y_test_pred,
                 average="weighted", zero_division=0), 4
))
print("F1-score (weighted):", round(
    f1_score(y_test, y_test_pred,
             average="weighted", zero_division=0), 4
))

print("\nTest classification report:")
print(
    classification_report(
        y_test,
        y_test_pred,
        zero_division=0
    )
)

print("\nConfusion matrix:")
print(confusion_matrix(y_test, y_test_pred))



joblib.dump(model, MODEL_DIR / "random_forest.pkl")

joblib.dump(
    {
        "feature_names": feature_names,
        "medians": medians.to_dict(),
        "target_column": target_col
    },
    MODEL_DIR / "preprocessing_info.pkl"
)

print("\nModel saved successfully!")
print("Model path:", MODEL_DIR / "random_forest.pkl")
print("Preprocessing information saved!")
