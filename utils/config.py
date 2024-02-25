import os

# Mail variables
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Replace with your email username
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Replace with your email password
MAIL_SERVER = 'smtp.gmail.com'  # Replace with your SMTP server address
IMAP_SERVER = "imap.gmail.com"  # Replace with your IMAP server address
MAIL_USE_SSL = True  # Enable SSL/TLS connection
MAIL_PORT = 465  # Use port 465 for SSL/TLS
IMAP_PORT = 993  # Use port 993 for SSL/TLS

# Constants
SEARCH_CRITERIA = ' '.join(['SUBJECT', '"test request"'])
attachments_dir = "..\\attachments"

# App variables
SECRET_KEY = os.environ.get('SECRET_KEY')

# SQL variables
SQLALCHEMY_DATABASE_URI = 'sqlite:///db_web.db'

# SAP variables
SAP_IP_ADDRESS = os.environ.get('SAP_IP_ADDRESS')  # Replace with your SAP IP ADDRESS
SAP_URL = os.environ.get('SAP_URL')  # Replace with your SAP URL


