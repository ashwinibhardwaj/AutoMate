from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
import pickle
import os
import time

def train_models(df):
    target_column = 'target'  # Update this to the actual name of your target column
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in the dataset")

    X = df.drop(columns=[target_column])
    y = df[target_column]

    if len(X) < 2:
        raise ValueError("Not enough samples to split the dataset.")

    # Check if the target variable is categorical or continuous
    if y.dtype in ['float64', 'int64']:
        unique_values = y.unique()
        if len(unique_values) <= 10:
            y = y.astype('int')  # For binary classification
            is_classification = True
        else:
            y = y.astype('float')  # For regression
            is_classification = False
    else:
        y = y.astype('category')
        is_classification = len(y.unique()) <= 2

    # Split the dataset
    test_size = 0.2 if len(X) > 1 else 0.1
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    if is_classification:
        # Classification scenario
        models = {
            'RandomForestClassifier': RandomForestClassifier(),
            'LogisticRegression': LogisticRegression(max_iter=10000),
            'SVC': SVC(),
            'KNeighborsClassifier': KNeighborsClassifier(),
            'GaussianNB': GaussianNB()
        }
        best_score = 0  # Higher is better for classification
        score_metric = 'accuracy'
    else:
        # Regression scenario
        models = {
            'RandomForestRegressor': RandomForestRegressor(),
            'LinearRegression': LinearRegression(),
            'SVR': SVR(),
            'KNeighborsRegressor': KNeighborsRegressor(),
        }
        best_score = float('inf')  # Lower is better for regression
        score_metric = 'mse'

    best_model = None
    model_details = []
    best_model_explanation = ""
    best_model_name = ""

    for name, model in models.items():
        try:
            start_time = time.time()
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            training_time = time.time() - start_time

            if is_classification:
                accuracy = round(accuracy_score(y_test, predictions), 2)
                precision = round(precision_score(y_test, predictions, average='weighted', zero_division=0), 2)
                recall = round(recall_score(y_test, predictions, average='weighted', zero_division=0), 2)
                f1 = round(f1_score(y_test, predictions, average='weighted'), 2)

                model_info = {
                    'name': name,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'training_time': round(training_time, 2),
                    'details': f'{name} achieved an accuracy of {accuracy:.2f}, precision of {precision:.2f}, recall of {recall:.2f}, and F1-score of {f1:.2f} in {training_time:.2f} seconds.'
                }
                score = accuracy  # Use accuracy as the score for classification

                if accuracy > best_score:
                    best_score = accuracy
                    best_model = model
                    best_model_name = name
                    best_model_explanation = model_info['details']

            else:
                mse = round(mean_squared_error(y_test, predictions), 2)
                r2 = round(r2_score(y_test, predictions), 2)

                model_info = {
                    'name': name,
                    'mse': mse,
                    'r2_score': r2,
                    'training_time': round(training_time, 2),
                    'details': f'{name} achieved an MSE of {mse:.2f} and R2 score of {r2:.2f} in {training_time:.2f} seconds.'
                }
                score = mse  # Use MSE as the score for regression

                if mse < best_score:
                    best_score = mse
                    best_model = model
                    best_model_name = name
                    best_model_explanation = model_info['details']

            model_details.append(model_info)

            # Save the model
            model_path = os.path.join('models', f'{name}.pkl')
            with open(model_path, 'wb') as file:
                pickle.dump(model, file)

        except Exception as e:
            print(f"Error training model {name}: {e}")

    if best_model:
        best_model_path = os.path.join('models', 'best_model.pkl')
        with open(best_model_path, 'wb') as file:
            pickle.dump(best_model, file)

    return {
        'best_model_name': best_model_name,
        'best_model_score': best_score,
        'best_model_details': best_model_explanation,
        'model_details': model_details
    }
