from flask import Flask, request, render_template, send_from_directory, url_for, flash, redirect, jsonify
import os
import pandas as pd
from sklearn.preprocessing import PowerTransformer
from sklearn.preprocessing import StandardScaler
from werkzeug.utils import secure_filename
from training import train_models
from flask import session

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24)) 

# Create folders if they do not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs('models', exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Configure Database (uses DATABASE_URL if set, otherwise falls back to SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure Flask-Mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"         # Adjust if using a different mail server
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config['MAIL_USERNAME'] = 'ashwini.10521@gmail.com'  
app.config['MAIL_PASSWORD'] = 'vlvu mqzu mibx txxr'  
app.config['MAIL_DEFAULT_SENDER'] = 'ashwini.10521@gmail.com' 

db = SQLAlchemy(app)
mail = Mail(app)

# Serializer for generating confirmation tokens
serializer = URLSafeTimedSerializer(app.secret_key)

# User model for Prime User registrations
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    prime_id = db.Column(db.String(50), unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    # If you want to store passwords, uncomment below:
    # password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


@app.route('/')
def index():
    # Render the upload page
    return render_template('index.html')

@app.route('/upload_page')
def upload_page():
    return render_template('upload.html')

@app.route('/registration_page')
def registration_page():
    return render_template('register.html')

# Registration endpoint to process the registration form
@app.route("/register", methods=["POST"])
def register():
    full_name = request.form.get("username")
    email = request.form.get("email")
    prime_id = request.form.get("prime_id")
    # For simplicity, password field is omitted in the HTML snippet provided.
    # If you include a password field, use:
    # password = request.form.get("password")

    # Check if a user with the same email or prime_id already exists
    if User.query.filter((User.email == email) | (User.prime_id == prime_id)).first():
        flash("User with the same email or Prime ID already exists.")
        return redirect(url_for("registration_page"))
    
    # Create the new user (email_verified defaults to False)
    new_user = User(full_name=full_name, email=email, prime_id=prime_id)
    # If using passwords, then:
    # new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()

    # Generate a token for email confirmation
    token = serializer.dumps(email, salt="email-confirmation")
    confirm_url = url_for("confirm_email", token=token, _external=True)

    # Send confirmation email
    msg = Message("Please confirm your email", recipients=[email])
    msg.body = f"Hi {full_name},\n\nThanks for registering as a Prime User on AutoMate!\n" \
               f"Please confirm your email address by clicking on the following link:\n{confirm_url}\n\n" \
               f"This link is valid for 1 hour."
    mail.send(msg)

    flash("Registration successful! Please check your email to confirm your account.")
    return redirect(url_for("registration_page"))

# Endpoint to handle email confirmation
@app.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = serializer.loads(token, salt="email-confirmation", max_age=3600)
    except SignatureExpired:
        flash("The confirmation link has expired. Please register again.")
        return redirect(url_for("registration_page"))
    except BadSignature:
        flash("Invalid confirmation token.")
        return redirect(url_for("registration_page"))

    user = User.query.filter_by(email=email).first_or_404()
    if user.email_verified:
        flash("Email already confirmed.")
    else:
        user.email_verified = True
        db.session.commit()
        flash("Email confirmed successfully! You can now Explore AutoMate.")
    return redirect(url_for("registration_page"))


@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if file is in the request
    if 'dataset' not in request.files:
        return jsonify({"error": "No file part in the request. Please try again."}), 400
    
    file = request.files['dataset']
    if file.filename == '':
        return jsonify({"error": "No file selected. Please try again."}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Read the file using pandas
        try:
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            return jsonify({"error": "Error reading file: " + str(e)}), 500

        # Check for required target column
        if 'target' not in df.columns:
            return jsonify({"error": "Uploaded file does not contain the required 'target' column. Please reupload a valid file."}), 400
        else:
            return jsonify({
                "message": "File is valid and contains the required 'target' column.",
                "filename": filename
            }), 200
    else:
        return jsonify({"error": "File type not allowed. Please upload a CSV or Excel file."}), 400


from sklearn.preprocessing import LabelEncoder

@app.route('/preprocess', methods=['POST'])
def preprocess_file():
    """
    This route performs essential preprocessing steps.
    Steps include:
      - Dropping duplicates.
      - Dropping 'id' and any 'Unnamed:' columns.
      - Filling missing values (numeric: median, categorical: mode).
      - (Optional) Transforming numeric columns using PowerTransformer.
      - (Optional) Standardizing numeric columns with StandardScaler.
      - (Optional) One-hot encoding categorical columns.
      - Automatically determining problem type for target column:
            * If unique count > 10, treat as regression.
            * Otherwise, treat as classification and encode target using LabelEncoder.
    """
    data = request.get_json()
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "No filename provided."}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if filename.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        return jsonify({"error": "Error reading file: " + str(e)}), 500

    logs = []
    logs.append(f"Original number of rows: {len(df)}")

    # 1. Drop duplicates
    before = len(df)
    df.drop_duplicates(inplace=True)
    after = len(df)
    logs.append(f"Dropped {before - after} duplicate rows.")

    # 1.1 Drop unwanted columns: id (case-insensitive) and columns starting with 'Unnamed:'
    drop_cols = [col for col in df.columns if col.lower() == 'id' or col.startswith('Unnamed:')]
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True)
        logs.append("Dropped columns: " + ", ".join(drop_cols))
    
    # Separate out the target column from preprocessing lists
    target_column = 'target'
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    if target_column in categorical_cols:
        categorical_cols.remove(target_column)
    elif target_column in numeric_cols:
        numeric_cols.remove(target_column)
    
    # 2. Fill missing values for numeric columns
    for col in numeric_cols:
        missing_count = df[col].isna().sum()
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        logs.append(f"Filled {missing_count} missing values in numeric column '{col}' with median: {median_val}.")
    
    # 3. Fill missing values for categorical columns
    for col in categorical_cols:
        missing_count = df[col].isna().sum()
        if not df[col].mode().empty:
            mode_val = df[col].mode()[0]
        else:
            mode_val = 'N/A'
        df[col] = df[col].fillna(mode_val)
        logs.append(f"Filled {missing_count} missing values in categorical column '{col}' with: {mode_val}.")

    # 4. (Optional) Transform numeric columns to approximate normal distribution
    if numeric_cols:
        try:
            pt = PowerTransformer(method='yeo-johnson')
            transformed = pt.fit_transform(df[numeric_cols])
            # 5. Standardize numeric columns
            scaler = StandardScaler()
            standardized = scaler.fit_transform(transformed)
            df[numeric_cols] = standardized
            logs.append("Applied PowerTransformer and StandardScaler to numeric columns.")
        except Exception as e:
            logs.append("Warning: Could not transform numeric columns: " + str(e))
    
    # 6. (Optional) One-hot encode categorical columns
    if categorical_cols:
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        logs.append("Applied one-hot encoding to categorical columns.")
    
    # 7. Automatically determine problem type for target column
    if target_column in df.columns:
        unique_count = df[target_column].nunique()
        if unique_count > 10:
            problem_type = "regression"
            logs.append(f"Determined problem type as regression since target column has {unique_count} unique values.")
        else:
            problem_type = "classification"
            logs.append(f"Determined problem type as classification since target column has {unique_count} unique values.")
        
        # For classification problems, encode the target column with LabelEncoder.
        if problem_type == "classification":
            le = LabelEncoder()
            df[target_column] = le.fit_transform(df[target_column].astype(str))
            logs.append("Encoded target column using LabelEncoder for classification.")
        else:
            logs.append("Skipped encoding target column for regression.")
    else:
        logs.append("Warning: Target column not found in the dataframe.")

    # Save the processed file
    processed_filename = "processed_" + filename
    processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
    try:
        df.to_csv(processed_filepath, index=False)
        logs.append("Processed file saved as " + processed_filename)
    except Exception as e:
        return jsonify({"error": "Error saving processed file: " + str(e)}), 500
    
    session['processed_filepath'] = processed_filepath
    download_url = url_for('download_processed')

    return jsonify({
        "message": "Preprocessing completed successfully.",
        "logs": logs,
        "download_url": download_url
    }), 200


@app.route('/download_processed')
def download_processed():
    processed_path = session.get('processed_filepath')
    if not processed_path:
        return jsonify({'error': 'No processed file available. Please preprocess first.'}), 400

    directory, filename = os.path.split(processed_path)
    if not os.path.isfile(processed_path):
        return jsonify({'error': 'Processed file not found on server.'}), 404

    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/download_model')
def download_model():
    model_path = session.get('best_model_path')
    if not model_path:
        return jsonify({'error': 'No trained model available. Please start training first.'}), 400

    directory, filename = os.path.split(model_path)
    if not os.path.isfile(model_path):
        return jsonify({'error': 'Model file not found on server.'}), 404

    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/start_training', methods=['POST'])
def start_training():
    try:
        # Retrieve the processed filename from the session
        processed_filepath = session.get('processed_filepath')
        if not processed_filepath:
            return jsonify({'error': "No processed file found. Please preprocess your file first."}), 400

        # Call your training function with the preprocessed file path
        training_results = train_models(processed_filepath)

        # ✅ Save model path in session
        if 'model_path' in training_results:
            session['best_model_path'] = training_results['model_path']

        return jsonify(training_results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
