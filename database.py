from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy with the database connection
db = SQLAlchemy()


# Create the Projet model
class Projet(db.Model):
    __tablename__ = 'projets'  # Specify table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    # Define one-to-many relationship with Request model (Projet has many Requests)
    requests = db.relationship('Request', backref='projet', lazy='dynamic')

    def __init__(self, name):
        self.name = name


# Create the Role model
class Role(db.Model):
    __tablename__ = 'roles'  # Specify table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # Define many-to-many relationship with User model (User has many Roles, Role has many Users)
    users = db.relationship('User', secondary='user_roles', backref='roles')

    def __init__(self, name):
        self.name = name


# Create a join table for the many-to-many relationship between users and roles
user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                      db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
                      )


# Create the User model
class User(db.Model):
    __tablename__ = 'users'  # Specify table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    verification_code = db.Column(db.String(20), nullable=True)
    # Define many-to-many relationship with Projet model (User has many Projets, Projet has many Users)
    projets = db.relationship('Projet', secondary='user_projets', backref='users')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


# Create a join table for the many-to-many relationship between users and projects
user_projets = db.Table('user_projets',
                        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                        db.Column('projet_id', db.Integer, db.ForeignKey('projets.id'))
                        )


# Create the Request model
class Request(db.Model):
    __tablename__ = 'requests'  # Specify table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.String(120), nullable=False, unique=True)
    type = db.Column(db.String(120), nullable=False)
    # Foreign key to the Projet model (One Request belongs to one Projet)
    projet_id = db.Column(db.Integer, db.ForeignKey('projets.id'))
    subject = db.Column(db.String(120), nullable=False)
    sender = db.Column(db.String(120), nullable=False)
    receiver = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    body = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.String, nullable=True)  # Store attachment paths as a string

    def __init__(self, num, type, projet_id, subject, sender, receiver, date, body, attachments):
        self.num = num
        self.type = type
        self.projet_id = projet_id
        self.subject = subject
        self.sender = sender
        self.receiver = receiver
        self.date = date
        self.body = body
        self.attachments = attachments


# Create the Dictionary model
class Dictionnaire(db.Model):
    __tablename__ = 'dictionnaire'  # Specify table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), unique=True, nullable=False)
    definition = db.Column(db.Text, nullable=False)  # Use db.Text for longer definitions
    is_deleted = db.Column(db.Boolean, default=False)

    def __init__(self, term, definition):
        self.term = term
        self.definition = definition
