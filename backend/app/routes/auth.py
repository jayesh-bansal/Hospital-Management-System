from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from .. import db
from ..models import User, Patient
bp = Blueprint('auth', __name__)
@bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter((User.username==username)|(User.email==username)).first()
    if not user or not user.check_password(password):
        return jsonify({'msg':'Bad credentials'}),401
    
    if not user.is_active:
        return jsonify({'msg':'Account disabled'}), 403
        
    if user.role == 'doctor' and user.doctor_profile and user.doctor_profile.is_blacklisted:
        return jsonify({'msg':'Account suspended'}), 403
        
    additional_claims = {'role': user.role}
    token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    return jsonify({'access_token': token, 'role': user.role, 'username': user.username, 'id': user.id})
@bp.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    if not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'msg':'missing fields'}),400
    if User.query.filter((User.username==data['username'])|(User.email==data['email'])).first():
        return jsonify({'msg':'user exists'}),400
    u = User(username=data['username'], email=data['email'], role='patient')
    u.set_password(data['password'])
    db.session.add(u); db.session.flush()
    p = Patient(user_id=u.id, phone=data.get('phone'))
    db.session.add(p); db.session.commit()
    return jsonify({'msg':'registered','id':u.id})

@bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user: return jsonify({'msg':'user not found'}), 404
    
    if request.method == 'GET':
        data = {
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        if user.role == 'patient' and user.patient_profile:
            data['phone'] = user.patient_profile.phone
        return jsonify(data)

    # PUT
    data = request.json or {}
    if 'email' in data: user.email = data['email']
    if 'password' in data and data['password']: user.set_password(data['password'])
    
    if user.role == 'patient' and 'phone' in data:
        if not user.patient_profile:
            # Create if missing? Should exist from register.
            p = Patient(user_id=user.id, phone=data['phone'])
            db.session.add(p)
        else:
            user.patient_profile.phone = data['phone']

    db.session.commit()
    return jsonify({'msg':'profile updated'})
