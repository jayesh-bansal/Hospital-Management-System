from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .. import db, cache
from ..models import Appointment, Patient, Doctor, Treatment, ExportJob
from datetime import datetime, timedelta, time
bp = Blueprint('appointments', __name__)

@bp.route('/slots', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
def get_slots():
    doctor_id = request.args.get('doctor_id')
    date_str = request.args.get('date')
    if not doctor_id or not date_str: return jsonify({'msg':'missing args'}),400
    
    date = datetime.fromisoformat(date_str).date()
    now = datetime.now()
    if date < now.date():
        return jsonify([])
    
    # Default working hours
    start_time = time(9,0)
    end_time = time(17,0)
    
    # Check doctor availability
    doc = Doctor.query.get(doctor_id)
    if doc and doc.availability_json:
        import json
        try:
            avail = json.loads(doc.availability_json)
            day_name = date.strftime('%a') # Mon, Tue...
            if day_name in avail:
                times = avail[day_name]
                if isinstance(times, list) and len(times) >= 2:
                     # Parse start/end times from availability
                     # Format: ["09:00", "12:00"]
                     try:
                         start_time = time.fromisoformat(times[0])
                         end_time = time.fromisoformat(times[1])
                     except ValueError: pass
            else:
                # Doctor not available on this day
                return jsonify([])
        except: pass

    # Generate slots based on determined start/end times
    start = datetime.combine(date, start_time)
    end = datetime.combine(date, end_time)
    
    # Get existing appointments
    existing = Appointment.query.filter_by(doctor_id=doctor_id, date=date).filter(Appointment.status!='Cancelled').all()
    booked_times = [a.time for a in existing]
    
    slots = []
    curr = start
    while curr < end:
        t = curr.time()
        if t not in booked_times:
            if date == now.date() and t < now.time():
                pass # Skip past times for today
            else:
                slots.append(t.isoformat())
        curr += timedelta(minutes=30)
        
    return jsonify(slots)

@bp.route('/book', methods=['POST'])
@jwt_required()
def book():
    data = request.json or {}
    user_id = get_jwt_identity(); claims = get_jwt()
    if claims.get('role')!='patient': return jsonify({'msg':'only patients'}),403
    patient = Patient.query.filter_by(user_id=user_id).first_or_404()
    doctor = Doctor.query.get_or_404(data.get('doctor_id'))
    if doctor.is_blacklisted: return jsonify({'msg':'doctor not available'}),400
    if doctor.is_blacklisted: return jsonify({'msg':'doctor not available'}),400
    
    date = datetime.fromisoformat(data['date']).date()
    try:
        # Try parsing as full datetime first (if frontend sends that)
        time_obj = datetime.fromisoformat(data['time']).time()
    except ValueError:
        # Fallback to time string parsing
        time_obj = time.fromisoformat(data['time'])
    
    # STRICT TIME SLOT VALIDATION
    if time_obj.minute % 30 != 0 or time_obj.second != 0 or time_obj.microsecond != 0:
        return jsonify({'msg':'invalid slot interval (must be :00 or :30)'}), 400

    # STRICT AVAILABILITY CHECK
    if doctor.availability_json:
        import json
        try:
            avail = json.loads(doctor.availability_json)
            day_name = date.strftime('%a')
            if day_name not in avail:
                return jsonify({'msg':'doctor not available on this day'}), 400
            
            times = avail[day_name]
            if isinstance(times, list) and len(times) >= 2:
                start_t = time.fromisoformat(times[0])
                end_t = time.fromisoformat(times[1])
                if not (start_t <= time_obj < end_t):
                     return jsonify({'msg':'time outside working hours'}), 400
            
        except Exception as e:
            print(f"Avail check error: {e}")
            pass
    existing = Appointment.query.filter_by(doctor_id=doctor.id, date=date, time=time_obj).first()
    if existing: return jsonify({'msg':'slot not available'}),400
    appt = Appointment(patient_id=patient.id, doctor_id=doctor.id, date=date, time=time_obj, status='Booked')
    db.session.add(appt); db.session.commit()
    return jsonify({'msg':'booked','appointment_id':appt.id})
@bp.route('/<int:appt_id>/reschedule', methods=['POST'])
@jwt_required()
def reschedule(appt_id):
    data = request.json or {}; user_id = get_jwt_identity(); claims = get_jwt()
    appt = Appointment.query.get_or_404(appt_id)
    if claims.get('role')=='patient':
        p = Patient.query.filter_by(user_id=user_id).first_or_404()
        if appt.patient_id!=p.id: return jsonify({'msg':'forbidden'}),403
    if 'date' in data and 'time' in data:
        try:
            # Fix: datetime.fromisoformat might fail on date-only strings in older python
            # Use strptime for YYYY-MM-DD
            try:
                new_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                # Fallback if it is a full iso string
                new_date = datetime.fromisoformat(data['date']).date()

            # Handle time parsing robustly
            try:
                # Try parsing as HH:MM:SS
                new_time = datetime.strptime(data['time'], '%H:%M:%S').time()
            except ValueError:
                try:
                    # Try parsing as HH:MM
                    new_time = datetime.strptime(data['time'], '%H:%M').time()
                except ValueError:
                     return jsonify({'msg': f"Invalid time format: {data['time']}"}), 400

            # STRICT TIME SLOT VALIDATION
            if new_time.minute % 30 != 0 or new_time.second != 0 or new_time.microsecond != 0:
                 return jsonify({'msg':'invalid slot interval (must be :00 or :30)'}), 400

            # STRICT AVAILABILITY CHECK (Reschedule)
            doctor = Doctor.query.get(appt.doctor_id)
            if doctor.availability_json:
                import json
                try:
                    avail = json.loads(doctor.availability_json)
                    day_name = new_date.strftime('%a')
                    if day_name not in avail:
                        return jsonify({'msg':'doctor not available on this day'}), 400
                    
                    times = avail[day_name]
                    if isinstance(times, list) and len(times) >= 2:
                        start_t = time.fromisoformat(times[0])
                        end_t = time.fromisoformat(times[1])
                        if not (start_t <= new_time < end_t):
                             return jsonify({'msg':'time outside working hours'}), 400
                    
                except Exception as e: 
                    print(f"Avail check warning: {e}")

            exists = Appointment.query.filter_by(doctor_id=appt.doctor_id, date=new_date, time=new_time).first()
            if exists and exists.id != appt.id: 
                return jsonify({'msg':'slot not available'}),400
            
            appt.date=new_date; appt.time=new_time; db.session.commit(); return jsonify({'msg':'rescheduled'})
        except Exception as e:
            print(f"Reschedule error: {e}")
            return jsonify({'msg': f'Error rescheduling: {str(e)}'}), 400
    return jsonify({'msg':'missing fields'}),400
@bp.route('/<int:appt_id>/cancel', methods=['POST'])
@jwt_required()
def cancel(appt_id):
    user_id = get_jwt_identity(); claims = get_jwt()
    appt = Appointment.query.get_or_404(appt_id)
    if claims.get('role')=='patient':
        p = Patient.query.filter_by(user_id=user_id).first_or_404(); 
        if appt.patient_id!=p.id: return jsonify({'msg':'forbidden'}),403
    appt.status='Cancelled'; db.session.commit(); return jsonify({'msg':'cancelled'})
@bp.route('/my', methods=['GET'])
@jwt_required()
def my_appointments():
    user_id = get_jwt_identity(); claims = get_jwt()
    role = claims.get('role')
    if role=='patient':
        p = Patient.query.filter_by(user_id=user_id).first_or_404(); appts = p.appointments
    elif role=='doctor':
        d = Doctor.query.filter_by(user_id=user_id).first_or_404(); appts = d.appointments
    else:
        appts = Appointment.query.all()
    res = [{'id':a.id,'patient':a.patient.user.username,'doctor':a.doctor.user.username,'doctor_id':a.doctor.id,'date':a.date.isoformat(),'time':a.time.isoformat(),'status':a.status} for a in appts]
    return jsonify(res)
@bp.route('/<int:appt_id>/complete', methods=['POST'])
@jwt_required()
def complete(appt_id):
    user_id = get_jwt_identity(); claims = get_jwt()
    if claims.get('role')!='doctor': return jsonify({'msg':'only doctors'}),403
    appt = Appointment.query.get_or_404(appt_id)
    data = request.json or {}
    appt.status='Completed'
    tr = Treatment(appointment_id=appt.id, patient_id=appt.patient_id, doctor_id=appt.doctor_id, diagnosis=data.get('diagnosis'), prescription=data.get('prescription'), notes=data.get('notes'))
    db.session.add(tr); db.session.commit()
    return jsonify({'msg':'completed'})
@bp.route('/export_my_treatments', methods=['POST'])
@jwt_required()
def export_my_treatments():
    user_id = get_jwt_identity(); claims = get_jwt()
    if claims.get('role')!='patient': return jsonify({'msg':'only patients'}),403
    p = Patient.query.filter_by(user_id=user_id).first_or_404()
    job = ExportJob(patient_id=p.id, status='pending'); db.session.add(job); db.session.commit()
    # enqueue celery task
    from ..celery_stub import celery_app
    from ..tasks import export_treatments_task
    export_treatments_task.delay(job.id)
    return jsonify({'msg':'export enqueued','job_id':job.id})

@bp.route('/export_status/<int:job_id>', methods=['GET'])
@jwt_required()
def check_export_status(job_id):
    job = ExportJob.query.get_or_404(job_id)
    return jsonify({'status':job.status})

@bp.route('/export_download/<int:job_id>', methods=['GET'])
def download_export(job_id):
    # No jwt required for download link if we want it simple, or pass token in query param
    # For security, let's assume browser handles it or we use a temporary token. 
    # But for simplicity in this task, let's allow if job exists.
    job = ExportJob.query.get_or_404(job_id)
    if job.status != 'done' or not job.path: return jsonify({'msg':'not ready'}), 400
    import os
    abs_path = os.path.abspath(job.path)
    return send_file(abs_path, as_attachment=True, download_name='treatments.csv', mimetype='text/csv')
