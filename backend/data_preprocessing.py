# import pandas as pd
# from sklearn.preprocessing import StandardScaler, LabelEncoder

# def preprocess_data(file_path):
#     messages = []

#     try:
#         df = pd.read_csv(file_path)
#     except Exception as e:
#         return None, f"Error reading file: {str(e)}"

#     # 1. Check for missing values
#     if df.isnull().values.any():
#         messages.append("Missing values detected. Filling missing values.")
#         df.fillna(df.mean(), inplace=True)
#     else:
#         messages.append("No missing values detected.")
    
#     # 2. Standardize numeric values
#     numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
#     if not numeric_columns.empty:
#         messages.append("Standardizing numeric values.")
#         scaler = StandardScaler()
#         df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
#     else:
#         messages.append("No numeric values to standardize.")
    
#     # 3. Convert character data to numeric data
#     categorical_columns = df.select_dtypes(include=['object']).columns
#     if not categorical_columns.empty:
#         messages.append("Converting character data to numeric form.")
#         label_encoders = {}
#         for col in categorical_columns:
#             le = LabelEncoder()
#             df[col] = le.fit_transform(df[col])
#             label_encoders[col] = le
#     else:
#         messages.append("No character data to convert.")
    
#     # Additional checks can be added here

#     messages.append("Data is ready for training.")

#     # Save the cleaned data to a new file
#     preprocessed_file_path = file_path.replace('.csv', '_preprocessed.csv')
#     df.to_csv(preprocessed_file_path, index=False)

#     return messages, preprocessed_file_path, None

import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_data(file_path):
    messages = []
    error = None
    preprocessed_file_path = None

    try:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
        messages.append("File loaded successfully.")
    except Exception as e:
        error = f"Error reading file: {str(e)}"
        return messages, preprocessed_file_path, error

    try:
        # Separate numeric and non-numeric columns
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        non_numeric_columns = df.select_dtypes(exclude=['float64', 'int64']).columns

        # Fill missing values for numeric columns with mean
        if df[numeric_columns].isnull().values.any():
            messages.append("Missing values detected in numeric columns. Filling missing values with column means.")
            df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
        else:
            messages.append("No missing values detected in numeric columns.")

        # Fill missing values for non-numeric columns with mode or a placeholder
        if df[non_numeric_columns].isnull().values.any():
            messages.append("Missing values detected in non-numeric columns. Filling missing values with 'Unknown'.")
            df[non_numeric_columns] = df[non_numeric_columns].fillna('Unknown')
        else:
            messages.append("No missing values detected in non-numeric columns.")
    except Exception as e:
        error = f"Error handling missing values: {str(e)}"
        return messages, preprocessed_file_path, error

    try:
        # Convert categorical data to numeric
        if not non_numeric_columns.empty:
            messages.append("Converting categorical data to numeric.")
            for col in non_numeric_columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
        else:
            messages.append("No categorical data found.")
    except Exception as e:
        error = f"Error encoding categorical data: {str(e)}"
        return messages, preprocessed_file_path, error

    try:
        # Standardize numeric values
        if not numeric_columns.empty:
            messages.append("Standardizing numeric values.")
            scaler = StandardScaler()
            df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
        else:
            messages.append("No numeric values to standardize.")
    except Exception as e:
        error = f"Error standardizing numeric data: {str(e)}"
        return messages, preprocessed_file_path, error

    messages.append("Data is ready for training.")

    try:
        # Save the cleaned data to a new file
        preprocessed_file_path = file_path.replace('.csv', '_preprocessed.csv')
        df.to_csv(preprocessed_file_path, index=False)
        messages.append(f"Preprocessed data saved to {preprocessed_file_path}.")
    except Exception as e:
        error = f"Error saving preprocessed data: {str(e)}"
        return messages, preprocessed_file_path, error

    return messages, preprocessed_file_path, error


