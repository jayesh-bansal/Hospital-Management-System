from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from .. import db
from ..models import User, Doctor, Patient, Appointment
import json

bp = Blueprint('admin', __name__)
def admin_only():
    claims = get_jwt(); return claims.get('role')=='admin'

@bp.route('/trigger_reminders', methods=['POST'])
@jwt_required()
def trigger_reminders():
    user_id = get_jwt_identity(); claims = get_jwt()
    if claims.get('role')!='admin': return jsonify({'msg':'admins only'}),403
    
    from ..tasks import daily_reminder_task
    # Trigger the task asynchronously (or synchronously if eager is set)
    daily_reminder_task.delay()
    
    return jsonify({'msg':'Daily reminders triggered successfully'})

@bp.route('/trigger_monthly_reports', methods=['POST'])
@jwt_required()
def trigger_monthly_reports():
    user_id = get_jwt_identity(); claims = get_jwt()
    if claims.get('role')!='admin': return jsonify({'msg':'admins only'}),403
    
    from ..tasks import monthly_report_task
    from ..models import Doctor
    
    # Optional: allow passing year/month in body
    data = request.json or {}
    year = data.get('year')
    month = data.get('month')
    
    doctors = Doctor.query.all()
    count = 0
    for doc in doctors:
        monthly_report_task.delay(doc.id, year, month)
        count += 1
        
    return jsonify({'msg':f'Triggered monthly reports for {count} doctors'})

@bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    if not admin_only(): return jsonify({'msg':'forbidden'}),403
    return jsonify({'doctors': Doctor.query.count(), 'patients': Patient.query.count(), 'appointments': Appointment.query.count()})

@bp.route('/doctors', methods=['POST'])
@jwt_required()
def add_doctor():
    if not admin_only():
        return jsonify({'msg': 'forbidden'}), 403

    data = request.json or {}

    # ---- SANITIZE ALL FIELDS ----
    def safe_str(value):
        if value is None:
            return ""
        try:
            return str(value).strip()
        except Exception:
            return ""

    username = safe_str(data.get("username"))
    email = safe_str(data.get("email"))
    specialization = safe_str(data.get("specialization"))
    # department_name = safe_str(data.get("department"))
    password = safe_str(data.get("password")) or "doctorpass"

    # VALIDATE username
    if not username:
        return jsonify({"msg": "username required"}), 400

    # CHECK IF EXISTS
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"msg": "user exists"}), 400

    # CREATE USER
    u = User(username=username, email=email, role="doctor")
    u.set_password(password)
    db.session.add(u)
    db.session.flush()

    # CREATE OR GET DEPARTMENT
    # dept = None
    # if department_name:
    #     dept = Department.query.filter_by(name=department_name).first()
    #     if not dept:
    #         dept = Department(name=department_name, description="")
    #         db.session.add(dept)
    #         db.session.flush()

    # HANDLE AVAILABILITY
    availability_raw = data.get("availability")
    availability_json = None

    if availability_raw:
        try:
            if isinstance(availability_raw, dict):
                availability_json = json.dumps(availability_raw)
            elif isinstance(availability_raw, str):
                availability_json = json.dumps(json.loads(availability_raw))
            else:
                availability_json = json.dumps({"note": str(availability_raw)})
        except Exception:
            availability_json = json.dumps({"note": "invalid format"})

    # CREATE DOCTOR
    d = Doctor(
        user_id=u.id,
        specialization=specialization,
        # department=dept,
        availability_json=availability_json
    )

    db.session.add(d)
    db.session.commit()

    return jsonify({"msg": "doctor created", "doctor_id": d.id})

# PUT /api/admin/doctors/<id>
@bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@jwt_required()
def edit_doctor(doctor_id):
    if not admin_only(): return jsonify({'msg':'forbidden'}),403
    d = Doctor.query.get_or_404(doctor_id)
    data = request.json or {}

    if 'specialization' in data: d.specialization = data['specialization']
    if 'is_blacklisted' in data: d.is_blacklisted = bool(data['is_blacklisted'])
    if 'username' in data: d.user.username = data['username'] # Edit Doctor Name

    # update availability if provided
    if 'availability' in data:
        availability = data.get('availability')
        try:
            if isinstance(availability, str):
                # validate JSON
                json.loads(availability)
                d.availability_json = availability
            else:
                d.availability_json = json.dumps(availability)
        except Exception:
            # fallback to storing a simple message
            d.availability_json = json.dumps({"note": str(availability)})

    db.session.commit()
    return jsonify({'msg':'updated'})

@bp.route('/patients/<int:patient_id>/blacklist', methods=['POST'])
@jwt_required()
def blacklist_patient(patient_id):
    if not admin_only(): return jsonify({'msg':'forbidden'}),403
    p = Patient.query.get_or_404(patient_id); p.user.is_active = False; db.session.commit(); return jsonify({'msg':'blacklisted'})

@bp.route('/patients/<int:patient_id>/unblacklist', methods=['POST'])
@jwt_required()
def unblacklist_patient(patient_id):
    if not admin_only(): return jsonify({'msg':'forbidden'}),403
    p = Patient.query.get_or_404(patient_id); p.user.is_active = True; db.session.commit(); return jsonify({'msg':'unblacklisted'})

@bp.route('/patients/<int:patient_id>', methods=['PUT'])
@jwt_required()
def edit_patient(patient_id):
    if not admin_only(): return jsonify({'msg':'forbidden'}),403
    p = Patient.query.get_or_404(patient_id)
    data = request.json or {}
    if 'username' in data: p.user.username = data['username']
    if 'phone' in data: p.phone = data['phone']
    db.session.commit()
    return jsonify({'msg':'updated'})

@bp.route('/search', methods=['GET'])
@jwt_required()
def search():
    if not admin_only(): return jsonify({'msg':'forbidden'}),403
    q = request.args.get('q','')
    docs = Doctor.query.join(Doctor.user).filter(User.username.ilike(f'%{q}%')).all()
    pats = Patient.query.join(Patient.user).filter(User.username.ilike(f'%{q}%')).all()
    
    doc_res = []
    for d in docs:
        # dept = d.department.name if d.department else None
        doc_res.append({
            'id':d.id,
            'username':d.user.username,
            'spec':d.specialization,
            'dept': None, # dept,
            'is_blacklisted': d.is_blacklisted,
            'availability': d.availability_json
        })
        
    pat_res = []
    for p in pats:
        pat_res.append({
            'id':p.id,
            'username':p.user.username,
            'is_active': p.user.is_active,
            'phone': p.phone
        })
        
    return jsonify({'doctors':doc_res, 'patients':pat_res})
@bp.route('/appointments', methods=['GET'])
@jwt_required()
def all_appointments():
    if not admin_only(): return jsonify({'msg':'forbidden'}),403
    appts = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    res = [{'id':a.id,'patient':a.patient.user.username,'doctor':a.doctor.user.username,'date':a.date.isoformat(),'time':a.time.isoformat(),'status':a.status} for a in appts]
    return jsonify(res)
