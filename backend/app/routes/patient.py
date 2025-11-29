from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import Patient, Doctor, Appointment, Treatment, User
from .. import db, cache
bp = Blueprint('patient', __name__)
@bp.route('/profile', methods=['GET','PUT'])
@jwt_required()
def profile():
    user_id = get_jwt_identity(); p = Patient.query.filter_by(user_id=user_id).first_or_404()
    if request.method=='GET':
        return jsonify({'username':p.user.username,'phone':p.phone,'email':p.user.email})
    data = request.json or {}; p.phone = data.get('phone',p.phone); db.session.commit(); return jsonify({'msg':'updated'})
@bp.route('/search_doctors', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, query_string=True)
def search_doctors():
    q = request.args.get('q','').strip()
    query = Doctor.query.join(Doctor.user).filter(Doctor.is_blacklisted==False)
    
    if q:
        # Search in username, email, OR specialization
        # Use join explicitly to avoid ambiguity if needed, but Doctor.user is already joined
        query = query.filter(
            User.username.ilike(f'%{q}%') | 
            User.email.ilike(f'%{q}%') | 
            Doctor.specialization.ilike(f'%{q}%')
        )
    
    docs = query.all()
    res = [{'id':d.id,'username':d.user.username,'spec':d.specialization,'department': None, 'availability': d.availability_json} for d in docs]
    return jsonify(res)
@bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    user_id = get_jwt_identity(); p = Patient.query.filter_by(user_id=user_id).first_or_404()
    treats = []
    for t in p.treatments:
        treats.append({'appointment_id':t.appointment_id,'diagnosis':t.diagnosis,'prescription':t.prescription,'notes':t.notes,'date':t.created_at.isoformat()})
    return jsonify(treats)

@bp.route('/departments', methods=['GET'])
@cache.cached(timeout=300)
def get_departments():
    # Return distinct specializations only
    specs = [r[0] for r in db.session.query(Doctor.specialization).distinct()]
    # depts = [d.name for d in Department.query.all()]
    # Combine and deduplicate
    all_tags = list(set(specs))
    return jsonify(all_tags)
