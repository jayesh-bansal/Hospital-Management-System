from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..models import Doctor, Appointment, Treatment, Patient
from .. import db
import json
bp = Blueprint('doctor', __name__)
@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    claims = get_jwt(); 
    if claims.get('role')!='doctor': return {'msg':'forbidden'},403
    user_id = get_jwt_identity(); d = Doctor.query.filter_by(user_id=user_id).first_or_404()
    appts = []
    for a in d.appointments:
        t = a.treatment
        appts.append({
            'id':a.id,
            'date':a.date.isoformat(),
            'time':a.time.isoformat(),
            'status':a.status,
            'patient':a.patient.user.username,
            'diagnosis': t.diagnosis if t else '',
            'prescription': t.prescription if t else ''
        })
    return jsonify({'appointments':appts, 'availability': d.availability_json})
@bp.route('/set_availability', methods=['POST'])
@jwt_required()
def set_availability():
    claims = get_jwt(); user_id = get_jwt_identity()
    if claims.get('role')!='doctor': return {'msg':'forbidden'},403
    data = request.json or {}; d = Doctor.query.filter_by(user_id=user_id).first_or_404()
    d.availability_json = json.dumps(data.get('availability', {})); db.session.commit(); return jsonify({'msg':'saved'})

@bp.route('/my_patients', methods=['GET'])
@jwt_required()
def my_patients():
    claims = get_jwt(); user_id = get_jwt_identity()
    if claims.get('role')!='doctor': return {'msg':'forbidden'},403
    d = Doctor.query.filter_by(user_id=user_id).first_or_404()
    # Get distinct patients from appointments
    # Get distinct patients from appointments
    pats = set([a.patient for a in d.appointments])
    res = [{'id':p.id,'username':p.user.username,'phone':p.phone,'gender':p.gender, 'email': p.user.email} for p in pats]
    return jsonify(res)

@bp.route('/appointments/<int:appt_id>/treatment', methods=['PUT'])
@jwt_required()
def update_treatment(appt_id):
    claims = get_jwt(); 
    if claims.get('role')!='doctor': return {'msg':'forbidden'},403
    appt = Appointment.query.get_or_404(appt_id)
    # Verify doctor owns this appointment
    user_id = get_jwt_identity()
    doctor = Doctor.query.filter_by(user_id=user_id).first_or_404()
    if appt.doctor_id != doctor.id: return {'msg':'forbidden'},403
    
    data = request.json or {}
    tr = appt.treatment
    if not tr: return {'msg':'treatment not found'},404
    
    if 'diagnosis' in data: tr.diagnosis = data['diagnosis']
    if 'prescription' in data: tr.prescription = data['prescription']
    db.session.commit()
    return jsonify({'msg':'updated'})
