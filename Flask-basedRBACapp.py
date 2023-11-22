from flask import Flask, g
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_principal import Principal, RoleNeed, identity_loaded, UserNeed

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rbac_example.db'
app.config['JWT_SECRET_KEY'] = 'super-secret'  # should put a secure key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)
principal = Principal(app)

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

# initialize the database
db.create_all()

# Roles
admin_role = RoleNeed('admin')
manager_role = RoleNeed('manager')
employee_role = RoleNeed('employee')
guest_role = RoleNeed('guest')

# Identity loader callback
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Add the user's roles to the identity
    user = g.identity.user
    if hasattr(user, 'roles'):
        for role in user.roles:
            identity.provides.add(RoleNeed(role.name))

# Object 1 resource
class OrganisationResource(Resource):
    @jwt_required()
    def get(self, org_id):
        organisation = OrganisationModel.query.get_or_404(org_id)
        return {'id': organisation.id, 'name': organisation.name}

# Object 2 resource
class EmployeeResource(Resource):
    @jwt_required()
    def get(self, emp_id):
        employee = EmployeeModel.query.get_or_404(emp_id)
        return {'id': employee.id, 'name': employee.name, 'organization_id': employee.organization_id}

# CRUD operations for object 1
class OrganisationCRUDResource(Resource):
    @jwt_required()
    @principal.require(admin_role)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name cannot be blank')
        args = parser.parse_args()

        organisation = OrganisationModel(name=args['name'])
        db.session.add(organisation)
        db.session.commit()

        return {'id': organisation.id, 'name': organisation.name}, 201

    @jwt_required()
    @principal.require(manager_role)
    def put(self, org_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name cannot be blank')
        args = parser.parse_args()

        organisation = OrganisationModel.query.get_or_404(org_id)
        organisation.name = args['name']
        db.session.commit()

        return {'id': organisation.id, 'name': organisation.name}

    @jwt_required()
    @principal.require(admin_role)
    def delete(self, org_id):
        organisation = OrganisationModel.query.get_or_404(org_id)
        db.session.delete(organisation)
        db.session.commit()

        return {'message': 'Organisation deleted'}

# CRUD operations for object 2
class EmployeeCRUDResource(Resource):
    @jwt_required()
    @principal.require(admin_role)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name cannot be blank')
        parser.add_argument('organization_id', type=int, required=True, help='Organization ID cannot be blank')
        args = parser.parse_args()

        employee = EmployeeModel(name=args['name'], organization_id=args['organization_id'])
        db.session.add(employee)
        db.session.commit()

        return {'id': employee.id, 'name': employee.name, 'organization_id': employee.organization_id}, 201

    @jwt_required()
    @principal.require(manager_role)
    def put(self, emp_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name cannot be blank')
        parser.add_argument('organization_id', type=int, required=True, help='Organization ID cannot be blank')
        args = parser.parse_args()

        employee = EmployeeModel.query.get_or_404(emp_id)
        employee.name = args['name']
        employee.organization_id = args['organization_id']
        db.session.commit()

        return {'id': employee.id, 'name': employee.name, 'organization_id': employee.organization_id}

    @jwt_required()
    @principal.require(admin_role)
    def delete(self, emp_id):
        employee = EmployeeModel.query.get_or_404(emp_id)
        db.session.delete(employee)
        db.session.commit()

        return {'message': 'Employee deleted'}

# API routes
api.add_resource(OrganisationResource, '/organisation/<int:org_id>')
api.add_resource(EmployeeResource, '/employee/<int:emp_id>')
api.add_resource(OrganisationCRUDResource, '/organisation')
api.add_resource(EmployeeCRUDResource, '/employee')

if __name__ == '__main__':
    app.run(debug=True)
