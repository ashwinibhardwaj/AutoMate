from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file, flash, session
import pandas as pd
import os
from werkzeug.utils import secure_filename
from data_preprocessing import preprocess_data
from model_training import train_models
import logging
from flask_mail import Mail, Message

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = 'models'
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

# Ensure the secret key is set
if not app.config['SECRET_KEY']:
    raise RuntimeError("No secret key set for Flask application")

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True   # Enable TLS
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'ashwini.10521@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'qqok qbiq phyh gwec'  # Your email password

mail = Mail(app)

# Ensure the uploads and models folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/data_page')
def data_page():
    return render_template('data_page.html')

@app.route('/preprocess_page')
def preprocess_page():
    return render_template('preprocessing_page.html')

@app.route('/about_page')
def about_page():
    return render_template('about_page.html')

@app.route('/feedback_page')
def feedback_page():
    return render_template('feedback_page.html')

@app.route('/desktop_page')
def desktop_page():
    return render_template('desktop_page.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            df = pd.read_csv(file_path, encoding='ISO-8859-1')
            if 'target' not in df.columns:
                return jsonify({'error': 'Missing required column: target'}), 400

            # File is valid
            return jsonify({'success': 'File is valid', 'file_path': file_path}), 200
        except Exception as e:
            app.logger.error(f"Error processing file: {e}")
            return jsonify({'error': f'Error processing file: {e}'}), 500

@app.route('/preprocess', methods=['POST'])
def preprocess():
    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path:
        return jsonify(error="File path not provided"), 400

    messages, preprocessed_file_path, error = preprocess_data(file_path)
    if error:
        return jsonify(error=error), 400
    session['preprocessed_file_path'] = preprocessed_file_path


    return jsonify({"messages": messages, "preprocessed_file_path": preprocessed_file_path})

@app.route('/train', methods=['POST'])
def train():
    data = request.get_json()
    preprocessed_file_path = data.get('preprocessed_file_path')

    if not preprocessed_file_path:
        return jsonify({'error': 'Preprocessed file path not provided'}), 400

    try:
        df = pd.read_csv(preprocessed_file_path)
        model_info = train_models(df)

        # Verify the model file exists
        model_path = os.path.join(app.config['MODEL_FOLDER'], 'best_model.pkl')
        if not os.path.exists(model_path):
            raise FileNotFoundError("Model file was not created")

        return jsonify({
            'success': 'Model training completed',
            'best_model_name': model_info['best_model_name'],
            'best_model_score': model_info['best_model_score'],
            'best_model_details': model_info['best_model_details'],
            'model_details': model_info['model_details']
        }), 200
    except Exception as e:
        app.logger.error(f"Error during model training: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_best_model')
def download_best_model():
    try:
        model_file = 'best_model.pkl'
        model_path = os.path.join(app.config['MODEL_FOLDER'], model_file)
        app.logger.info(f"Attempting to download file from: {model_path}")

        # Ensure the file exists
        if not os.path.isfile(model_path):
            app.logger.error(f"File not found: {model_path}")
            return jsonify({'error': 'Model file not found'}), 404

        # Send the file for download
        return send_file(model_path, as_attachment=True, download_name=model_file)
    
    except Exception as e:
        app.logger.error(f"Error downloading model file: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Send email
        msg = Message(subject='Feedback from Automate by {}'.format(name),
                      sender=email,
                      recipients=['ashwini.10521@gmail.com']) 
        msg.body = f'Name: {name}\nEmail: {email}\nMessage:\n{message}'

        try:
            mail.send(msg)
            app.logger.info("Email sent successfully.")
            flash('Feedback submitted successfully! Thank you.', 'success')
        except Exception as e:
            app.logger.error(f"An error occurred while sending the email: {e}")
            flash(f'An error occurred while sending the email: {e}', 'danger')

        return redirect(url_for('feedback'))

    return render_template('feedback_page.html')

@app.route('/download_preprocessed_file', methods=['POST'])
def download_preprocessed_file():
    # Retrieve the preprocessed file path from session
    preprocessed_file_path = session.get('preprocessed_file_path')

    if not preprocessed_file_path:
        return "No preprocessed file path found", 400

    try:
        return send_file(preprocessed_file_path, as_attachment=True)
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
