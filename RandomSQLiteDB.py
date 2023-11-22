from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///random_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Object 1: Organisation
class OrganisationModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Object 2: Employee
class EmployeeModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organisation_model.id'))
    organization = db.relationship('OrganisationModel', backref='employees')

# Initialize the database
db.create_all()

# Create random data using Faker
fake = Faker()

# Create Organisations
for _ in range(5):
    organisation = OrganisationModel(name=fake.company())
    db.session.add(organisation)

# Create Employees with random organisations
organisations = OrganisationModel.query.all()
for _ in range(10):
    employee = EmployeeModel(name=fake.name(), organization=random.choice(organisations))
    db.session.add(employee)

# Commit the changes to the database
db.session.commit()

print("Random SQLite Database created successfully.")
