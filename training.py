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
import pandas as pd

def train_models(preprocessed_file_path):
    # Load the preprocessed data
    df = pd.read_csv(preprocessed_file_path)
    
    target_column = 'target'  # Update if needed
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in the dataset")

    X = df.drop(columns=[target_column])
    y = df[target_column]

    if len(X) < 2:
        raise ValueError("Not enough samples to split the dataset.")

    # Determine whether classification or regression based on target values
    if y.dtype in ['float64', 'int64']:
        unique_values = y.unique()
        if len(unique_values) <= 10:
            y = y.astype('int')
            is_classification = True
        else:
            y = y.astype('float')
            is_classification = False
    else:
        y = y.astype('category')
        is_classification = len(y.unique()) <= 2

    test_size = 0.2 if len(X) > 1 else 0.1
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    if is_classification:
        models = {
            'RandomForestClassifier': RandomForestClassifier(),
            'LogisticRegression': LogisticRegression(max_iter=10000),
            'SVC': SVC(),
            'KNeighborsClassifier': KNeighborsClassifier(),
            'GaussianNB': GaussianNB()
        }
        best_score = 0  # For classification, higher is better
    else:
        models = {
            'RandomForestRegressor': RandomForestRegressor(),
            'LinearRegression': LinearRegression(),
            'SVR': SVR(),
            'KNeighborsRegressor': KNeighborsRegressor(),
        }
        best_score = float('inf')  # For regression, lower is better

    best_model = None
    best_model_name = ""
    best_model_explanation = ""
    model_details = []
    best_model_path = None

    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)

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

                score = accuracy
                details = (f"{name} achieved an accuracy of {accuracy:.2f}, "
                           f"precision of {precision:.2f}, recall of {recall:.2f}, "
                           f"and F1-score of {f1:.2f} in {training_time:.2f} seconds.")

                model_info = {
                    'name': name,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'training_time': round(training_time, 2),
                    'details': details
                }

                if accuracy > best_score:
                    best_score = accuracy
                    best_model = model
                    best_model_name = name
                    best_model_explanation = details
            else:
                mse = round(mean_squared_error(y_test, predictions), 2)
                r2 = round(r2_score(y_test, predictions), 2)

                score = r2
                details = (f"{name} achieved an MSE of {mse:.2f} and R2 score of {r2:.2f} "
                           f"in {training_time:.2f} seconds.")

                model_info = {
                    'name': name,
                    'mse': mse,
                    'r2_score': r2,
                    'training_time': round(training_time, 2),
                    'details': details
                }

                if mse < best_score:
                    best_score = mse
                    best_model = model
                    best_model_name = name
                    best_model_explanation = details

            model_details.append(model_info)

            # Save individual model
            model_file = os.path.join('models', f'{name}.pkl')
            with open(model_file, 'wb') as file:
                pickle.dump(model, file)
        except Exception as e:
            print(f"Error training model {name}: {e}")

    # Save the best model if found
    # Save the best model if found
    if best_model:
        base_filename = os.path.splitext(os.path.basename(preprocessed_file_path))[0]
        best_model_filename = f"{base_filename}_bestmodel.pkl"
        best_model_path = os.path.join('models', best_model_filename)
        with open(best_model_path, 'wb') as file:
            pickle.dump(best_model, file)


    return {
        'best_model_name': best_model_name,
        'best_model_score': best_score,
        'best_model_details': best_model_explanation,
        'model_details': model_details,
        'model_path': best_model_path
    }
