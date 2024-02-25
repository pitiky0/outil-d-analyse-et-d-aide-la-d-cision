import subprocess
from routes.auth import *
from flask import Flask, jsonify
from routes.dictionnaire import *
from flask_mail import Mail, Message
from utils.email_listener import listen_for_new_emails
from utils.config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, \
    MAIL_USE_SSL, MAIL_PASSWORD, SAP_URL, SAP_IP_ADDRESS

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configure database URI here
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

# Configure Flask-Mail with imported settings
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_SSL'] = MAIL_USE_SSL
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_DEFAULT_SENDER'] = MAIL_USERNAME
app.config['MAIL_ASCII_ATTACHMENTS'] = True
app.config['DEBUG'] = True

mail = Mail(app)  # Initialize Flask-Mail with the app
db.init_app(app)  # Initialize SQLAlchemy with the app

with app.app_context():
    db.create_all()  # create all tables if not exists


def send_verification_email(email, verification_code):
    try:
        msg = Message(
            'Password Reset Verification',
            recipients=[email],
            html=render_template('auth/verify-email.html', verification_code=verification_code)  # Set HTML content
        )
        mail.send(msg)
    except Exception as e:
        raise e
    return redirect(url_for('verify_password_reset', email=email))


def index():
    latest_reviews = [
        {'date': '2024-02-17', 'action': 'Reviewed PCR request #123'},
        {'date': '2024-02-16', 'action': 'Reviewed DFC request #456'},
        {'date': '2024-02-15', 'action': 'Reviewed PCR request #789'},
    ]
    return render_template('index.html', latest_reviews=latest_reviews)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.route('/review_history')
def review_history():
    # Add logic here to fetch review history data from your database or any other source
    # For demonstration purposes, let's assume we have a list of review history items
    review_history_items = [
        {'date': '2024-02-17', 'action': 'Reviewed PCR request #123'},
        {'date': '2024-02-16', 'action': 'Reviewed DFC request #456'},
        {'date': '2024-02-15', 'action': 'Reviewed PCR request #789'},
    ]
    return render_template('review_history.html', review_history_items=review_history_items)


@app.route('/submit_pcr_request')
def submit_pcr_request():
    # Logic for submitting PCR request goes here
    return render_template('submit_pcr_request.html')


@app.route('/submit_dfc_request')
def submit_dfc_request():
    # Logic for submitting DFC request goes here
    return render_template('submit_dfc_request.html')


@app.route("/check_sap_availability", methods=['GET', 'POST'])
def check_sap_availability():
    if request.method == "GET":
        return render_template('sap_page.html')
    if request.method == "POST":
        try:
            # Check if SAP IP address is reachable
            result = subprocess.run(['ping', SAP_IP_ADDRESS], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:  # IP address reachable
                return jsonify({"status": "ok"})
            else:
                return jsonify({"status": "error", "message": "System unavailable"}), 500
        except Exception:
            return jsonify({"status": "error", "message": "Internal error"}), 500


@app.route("/sap_url")
def sap_url():
    return redirect(SAP_URL)


@app.route('/change_engineer_formation')
def change_engineer_formation():
    return render_template('formation.html')


@app.route('/process_emails')
def process_emails():
    try:
        listen_for_new_emails()
        return 'Emails processed successfully!'
    except Exception as e:
        print(f"Error processing emails: {e}")
        return 'An error occurred during email processing.'


# index routes
app.add_url_rule('/', 'index', index)
app.add_url_rule('/index', 'index', index)

# dictionary routes
app.add_url_rule('/dictionary/index', 'dictionnaire', dictionnaire)
app.add_url_rule('/dictionary/show_term/<string:id>', 'show_term', show_term, methods=['GET'])
app.add_url_rule('/dictionary/add_term', 'add_term', add_term, methods=['GET', 'POST'])
app.add_url_rule('/dictionary/edit_term/<string:id>', 'edit_term', edit_term, methods=['GET', 'POST'])
app.add_url_rule('/dictionary/delete_term/<string:id>', 'delete_term', delete_term, methods=['POST'])

# Auth routes
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/signup', 'signup', signup, methods=['GET', 'POST'])
app.add_url_rule('/forgot-password', 'forgot_password', forgot_password, methods=['GET', 'POST'])
app.add_url_rule('/password-reset/<string:email>', 'verify_password_reset', verify_password_reset,
                 methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True)
