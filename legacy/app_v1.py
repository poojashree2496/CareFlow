from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import or_
import os, re
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-this-demo-secret-before-deployment')
def database_uri():
    """Resolve local SQLite or a Supabase PostgreSQL connection URL."""
    uri = os.environ.get('DATABASE_URL', '').strip()
    if not uri:
        return 'sqlite:///' + os.path.join(BASE_DIR, 'hospital.db')
    # Supabase sometimes supplies postgres:// or postgresql:// URLs. Use psycopg v3.
    if uri.startswith('postgres://'):
        uri = 'postgresql://' + uri[len('postgres://'):]
    if uri.startswith('postgresql://'):
        uri = 'postgresql+psycopg://' + uri[len('postgresql://'):]
    return uri

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri()
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.String(10), default='')
    gender = db.Column(db.String(30), default='Not specified')
    phone = db.Column(db.String(30), default='')
    email = db.Column(db.String(120), default='')
    blood_group = db.Column(db.String(5), default='')
    allergies = db.Column(db.Text, default='')
    emergency_contact = db.Column(db.String(120), default='')
    medical_history = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), default='General')
    phone = db.Column(db.String(30), default='')
    available = db.Column(db.Boolean, default=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.String(10), nullable=False)
    appointment_time = db.Column(db.String(5), nullable=False)
    reason = db.Column(db.String(300), default='')
    status = db.Column(db.String(30), default='Scheduled')
    patient = db.relationship('Patient')
    doctor = db.relationship('Doctor')

class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    ward = db.Column(db.String(80), nullable=False)
    bed = db.Column(db.String(30), default='Unassigned')
    admitted_on = db.Column(db.String(10), nullable=False)
    discharged_on = db.Column(db.String(10), default='')
    status = db.Column(db.String(30), default='Admitted')
    notes = db.Column(db.Text, default='')
    patient = db.relationship('Patient')

class LabReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    test_name = db.Column(db.String(120), nullable=False)
    sample_date = db.Column(db.String(10), nullable=False)
    result = db.Column(db.Text, default='Pending')
    status = db.Column(db.String(30), default='Pending')
    ordered_by = db.Column(db.String(120), default='')
    patient = db.relationship('Patient')

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(80), default='General')
    stock = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    unit_price = db.Column(db.Float, default=0)
    expiry_date = db.Column(db.String(10), default='')

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_name = db.Column(db.String(120), default='')
    medicine = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(120), default='As directed by clinician')
    instructions = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient')

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    consultation = db.Column(db.Float, default=0)
    laboratory = db.Column(db.Float, default=0)
    pharmacy = db.Column(db.Float, default=0)
    room = db.Column(db.Float, default=0)
    insurance_provider = db.Column(db.String(120), default='')
    insurance_status = db.Column(db.String(40), default='Not submitted')
    paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient')
    @property
    def total(self): return round((self.consultation or 0)+(self.laboratory or 0)+(self.pharmacy or 0)+(self.room or 0),2)

class RadiologyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    modality = db.Column(db.String(50), nullable=False)
    study_date = db.Column(db.String(10), nullable=False)
    findings = db.Column(db.Text, default='')
    report_status = db.Column(db.String(30), default='Draft')
    patient = db.relationship('Patient')

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(120), nullable=False)
    details = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def log(action, details=''):
    db.session.add(AuditLog(action=action, details=details[:1000]))

def next_patient_code():
    return 'P-' + datetime.utcnow().strftime('%y%m%d') + '-' + os.urandom(2).hex().upper()

def payload():
    return request.get_json(silent=True) or request.form

def need(data, *keys):
    missing = [k for k in keys if not str(data.get(k, '')).strip()]
    if missing: raise ValueError('Required fields: ' + ', '.join(missing))

def get_patient(pid):
    p = db.session.get(Patient, pid)
    if not p: raise ValueError('Patient not found')
    return p

@app.route('/')
def index():
    q = request.args.get('q','').strip()
    patients_query = Patient.query
    if q: patients_query = patients_query.filter(or_(Patient.name.ilike(f'%{q}%'), Patient.patient_code.ilike(f'%{q}%'), Patient.phone.ilike(f'%{q}%')))
    stats = {'patients': Patient.query.count(), 'doctors': Doctor.query.count(), 'appointments': Appointment.query.filter_by(status='Scheduled').count(), 'admissions': Admission.query.filter_by(status='Admitted').count(), 'pending_labs': LabReport.query.filter_by(status='Pending').count(), 'low_stock': Medicine.query.filter(Medicine.stock <= Medicine.reorder_level).count()}
    return render_template('index.html', stats=stats, patients=patients_query.order_by(Patient.created_at.desc()).limit(100).all(), doctors=Doctor.query.order_by(Doctor.name).all(), appointments=Appointment.query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).limit(100).all(), admissions=Admission.query.filter_by(status='Admitted').all(), labs=LabReport.query.order_by(LabReport.sample_date.desc()).limit(100).all(), medicines=Medicine.query.order_by(Medicine.name).all(), prescriptions=Prescription.query.order_by(Prescription.created_at.desc()).limit(100).all(), bills=Bill.query.order_by(Bill.created_at.desc()).limit(100).all(), radiology=RadiologyRecord.query.order_by(RadiologyRecord.study_date.desc()).limit(100).all(), audit=AuditLog.query.order_by(AuditLog.created_at.desc()).limit(12).all(), today=date.today().isoformat(), q=q)

@app.route('/api/patients', methods=['POST'])
def create_patient():
    d=payload()
    try:
        need(d,'name')
        p=Patient(patient_code=next_patient_code(), name=d['name'].strip(), dob=d.get('dob',''), gender=d.get('gender','Not specified'), phone=d.get('phone',''), email=d.get('email',''), blood_group=d.get('blood_group',''), allergies=d.get('allergies',''), emergency_contact=d.get('emergency_contact',''), medical_history=d.get('medical_history',''))
        db.session.add(p); db.session.flush(); log('Patient registered', f'{p.patient_code}: {p.name}'); db.session.commit()
        return jsonify(ok=True,message='Patient registered',id=p.id,patient_code=p.patient_code)
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/patients/<int:pid>', methods=['GET','PUT','DELETE'])
def patient_detail(pid):
    try:
        p=get_patient(pid)
        if request.method=='GET': return jsonify(id=p.id,patient_code=p.patient_code,name=p.name,dob=p.dob,gender=p.gender,phone=p.phone,email=p.email,blood_group=p.blood_group,allergies=p.allergies,emergency_contact=p.emergency_contact,medical_history=p.medical_history)
        if request.method=='PUT':
            d=payload()
            for k in ['name','dob','gender','phone','email','blood_group','allergies','emergency_contact','medical_history']:
                if k in d: setattr(p,k,d[k])
            log('Patient updated',p.patient_code); db.session.commit(); return jsonify(ok=True,message='Patient updated')
        if Appointment.query.filter_by(patient_id=pid).first() or Admission.query.filter_by(patient_id=pid).first(): return jsonify(ok=False,error='Patient has linked clinical records and cannot be deleted. Archive is not implemented in this demo.'),409
        db.session.delete(p); log('Patient deleted',p.patient_code); db.session.commit(); return jsonify(ok=True,message='Patient deleted')
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/doctors', methods=['POST'])
def create_doctor():
    d=payload()
    try:
        need(d,'name','specialty'); doc=Doctor(name=d['name'].strip(),specialty=d['specialty'].strip(),department=d.get('department','General'),phone=d.get('phone',''))
        db.session.add(doc); log('Doctor added',doc.name); db.session.commit(); return jsonify(ok=True,message='Doctor added')
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    d=payload()
    try:
        need(d,'patient_id','doctor_id','appointment_date','appointment_time')
        p=get_patient(int(d['patient_id'])); doc=db.session.get(Doctor,int(d['doctor_id']))
        if not doc or not doc.available: raise ValueError('Selected doctor is unavailable')
        if d['appointment_date'] < date.today().isoformat(): raise ValueError('Appointment date cannot be in the past')
        conflict=Appointment.query.filter_by(doctor_id=doc.id,appointment_date=d['appointment_date'],appointment_time=d['appointment_time'],status='Scheduled').first()
        if conflict: raise ValueError('This doctor already has an appointment at that time')
        a=Appointment(patient_id=p.id,doctor_id=doc.id,appointment_date=d['appointment_date'],appointment_time=d['appointment_time'],reason=d.get('reason',''))
        db.session.add(a); log('Appointment scheduled',f'{p.patient_code} with {doc.name} on {a.appointment_date} {a.appointment_time}'); db.session.commit(); return jsonify(ok=True,message='Appointment scheduled')
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/appointments/<int:aid>', methods=['PATCH','DELETE'])
def appointment_update(aid):
    a=db.session.get(Appointment,aid)
    if not a: return jsonify(ok=False,error='Appointment not found'),404
    d=payload()
    if request.method=='DELETE': a.status='Cancelled'
    else:
        status=d.get('status','')
        if status not in ['Scheduled','Completed','Cancelled','No-show']: return jsonify(ok=False,error='Invalid status'),400
        a.status=status
    log('Appointment updated',f'#{aid}: {a.status}'); db.session.commit(); return jsonify(ok=True,message='Appointment updated')

@app.route('/api/admissions', methods=['POST'])
def create_admission():
    d=payload()
    try:
        need(d,'patient_id','ward','admitted_on'); p=get_patient(int(d['patient_id']))
        if Admission.query.filter_by(patient_id=p.id,status='Admitted').first(): raise ValueError('Patient already has an active admission')
        a=Admission(patient_id=p.id,ward=d['ward'],bed=d.get('bed','Unassigned'),admitted_on=d['admitted_on'],notes=d.get('notes',''))
        db.session.add(a); log('Patient admitted',f'{p.patient_code}, {a.ward} / {a.bed}'); db.session.commit(); return jsonify(ok=True,message='Admission recorded')
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/admissions/<int:aid>/discharge', methods=['POST'])
def discharge(aid):
    a=db.session.get(Admission,aid)
    if not a: return jsonify(ok=False,error='Admission not found'),404
    a.status='Discharged'; a.discharged_on=date.today().isoformat(); log('Patient discharged',a.patient.patient_code); db.session.commit(); return jsonify(ok=True,message='Patient discharged')

@app.route('/api/labs', methods=['POST'])
def create_lab():
    d=payload()
    try:
        need(d,'patient_id','test_name','sample_date'); p=get_patient(int(d['patient_id']))
        lab=LabReport(patient_id=p.id,test_name=d['test_name'],sample_date=d['sample_date'],result=d.get('result','Pending'),status='Completed' if d.get('result','').strip() else 'Pending',ordered_by=d.get('ordered_by',''))
        db.session.add(lab); log('Lab test created',f'{p.patient_code}: {lab.test_name}'); db.session.commit(); return jsonify(ok=True,message='Lab record created')
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/labs/<int:lid>', methods=['PATCH'])
def update_lab(lid):
    lab=db.session.get(LabReport,lid)
    if not lab: return jsonify(ok=False,error='Lab record not found'),404
    d=payload(); lab.result=d.get('result',lab.result); lab.status='Completed' if lab.result and lab.result!='Pending' else 'Pending'; log('Lab report updated',f'#{lid}: {lab.status}'); db.session.commit(); return jsonify(ok=True,message='Lab report updated')

@app.route('/api/medicines', methods=['POST'])
def create_medicine():
    d=payload()
    try:
        need(d,'name'); stock=int(d.get('stock',0)); price=float(d.get('unit_price',0))
        if stock<0 or price<0: raise ValueError('Stock and price cannot be negative')
        if Medicine.query.filter_by(name=d['name'].strip()).first(): raise ValueError('Medicine already exists')
        m=Medicine(name=d['name'].strip(),category=d.get('category','General'),stock=stock,reorder_level=int(d.get('reorder_level',10)),unit_price=price,expiry_date=d.get('expiry_date',''))
        db.session.add(m); log('Medicine added',m.name); db.session.commit(); return jsonify(ok=True,message='Medicine added')
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/medicines/<int:mid>', methods=['PATCH'])
def update_medicine(mid):
    m=db.session.get(Medicine,mid)
    if not m: return jsonify(ok=False,error='Medicine not found'),404
    d=payload()
    try:
        if 'stock' in d:
            stock=int(d['stock'])
            if stock<0: raise ValueError('Stock cannot be negative')
            m.stock=stock
        if 'unit_price' in d:
            price=float(d['unit_price'])
            if price<0: raise ValueError('Price cannot be negative')
            m.unit_price=price
        if 'expiry_date' in d: m.expiry_date=d['expiry_date']
        log('Medicine updated',m.name); db.session.commit(); return jsonify(ok=True,message='Inventory updated')
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/prescriptions', methods=['POST'])
def create_prescription():
    d=payload()
    try:
        need(d,'patient_id','medicine'); p=get_patient(int(d['patient_id']))
        rx=Prescription(patient_id=p.id,doctor_name=d.get('doctor_name',''),medicine=d['medicine'],dosage=d.get('dosage','As directed by clinician'),instructions=d.get('instructions',''))
        db.session.add(rx); log('Prescription recorded',f'{p.patient_code}: {rx.medicine}'); db.session.commit(); return jsonify(ok=True,message='Prescription recorded')
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/radiology', methods=['POST'])
def create_radiology():
    d=payload()
    try:
        need(d,'patient_id','modality','study_date'); p=get_patient(int(d['patient_id']))
        r=RadiologyRecord(patient_id=p.id,modality=d['modality'],study_date=d['study_date'],findings=d.get('findings',''),report_status='Final' if d.get('findings','').strip() else 'Draft')
        db.session.add(r); log('Radiology record created',f'{p.patient_code}: {r.modality}'); db.session.commit(); return jsonify(ok=True,message='Radiology record created')
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/bills', methods=['POST'])
def create_bill():
    d=payload()
    try:
        need(d,'patient_id','description'); p=get_patient(int(d['patient_id']))
        values={k:float(d.get(k,0) or 0) for k in ['consultation','laboratory','pharmacy','room']}
        if any(v<0 for v in values.values()): raise ValueError('Charges cannot be negative')
        b=Bill(patient_id=p.id,description=d['description'],insurance_provider=d.get('insurance_provider',''),insurance_status=d.get('insurance_status','Not submitted'),**values)
        db.session.add(b); log('Bill created',f'{p.patient_code}: ₹{b.total:.2f}'); db.session.commit(); return jsonify(ok=True,message=f'Bill created. Total ₹{b.total:.2f}',total=b.total)
    except Exception as e: db.session.rollback(); return jsonify(ok=False,error=str(e)),400

@app.route('/api/bills/<int:bid>', methods=['PATCH'])
def update_bill(bid):
    b=db.session.get(Bill,bid)
    if not b: return jsonify(ok=False,error='Bill not found'),404
    d=payload()
    if 'paid' in d: b.paid=str(d['paid']).lower() in ['true','1','yes','paid']
    if 'insurance_status' in d and d['insurance_status'] in ['Not submitted','Submitted','Approved','Rejected','Pending']: b.insurance_status=d['insurance_status']
    log('Billing status updated',f'#{bid}'); db.session.commit(); return jsonify(ok=True,message='Bill updated')

@app.route('/api/ai/disease-prediction', methods=['POST'])
def disease_prediction():
    d=payload(); symptoms=[s.strip().lower() for s in re.split(r'[,;]',d.get('symptoms','')) if s.strip()]
    if not symptoms: return jsonify(ok=False,error='Enter at least one symptom.'),400
    # Educational symptom-to-topic matching only; intentionally not a clinical prediction model.
    rules={'fever':['fever','infection'], 'cough':['respiratory illness','allergy'], 'headache':['headache causes','migraine'], 'sneezing':['allergy','upper respiratory irritation'], 'fatigue':['fatigue causes','sleep or stress-related factors'], 'chest pain':['urgent assessment required'], 'shortness of breath':['urgent assessment required'], 'rash':['skin irritation','allergy']}
    topics=[]
    for s in symptoms:
        for key,vals in rules.items():
            if key in s and vals not in topics: topics.extend(vals)
    if not topics: topics=['A clinician should assess the symptoms in context']
    urgent=any(any(term in s for term in ['chest pain','shortness of breath','difficulty breathing','fainting','stroke']) for s in symptoms)
    return jsonify(ok=True,notice='Educational triage aid only. Not a diagnosis and not a validated prediction model.',topics=topics,urgent=urgent,advice='Seek emergency care now for severe or sudden symptoms.' if urgent else 'Arrange evaluation with a qualified clinician, especially if symptoms persist or worsen.')

@app.route('/api/ai/prescription-explanation', methods=['POST'])
def prescription_explanation():
    d=payload()
    if not str(d.get('prescription','')).strip(): return jsonify(ok=False,error='Enter the prescription text.'),400
    text=d['prescription'].strip()
    return jsonify(ok=True,explanation='Plain-language reading aid (not verified medical advice):\n\n'+text+'\n\nPlease confirm the medicine name, dose, timing, duration, and whether it should be taken with food with your pharmacist or prescribing clinician. Do not change or stop a medicine based on this explanation alone.')

@app.route('/api/ai/interactions', methods=['POST'])
def interaction_check():
    d=payload(); meds=[x.strip().lower() for x in re.split(r'[,;\n]',d.get('medicines','')) if x.strip()]
    if len(meds)<2: return jsonify(ok=False,error='Enter at least two medicine names separated by commas.'),400
    # Small illustrative list, not a comprehensive drug database.
    pairs=[({'warfarin','ibuprofen'},'Potentially increased bleeding risk'),({'sildenafil','nitroglycerin'},'Potentially dangerous blood-pressure drop'),({'sertraline','tramadol'},'Potential serotonin toxicity risk'),({'lisinopril','potassium chloride'},'Potentially elevated potassium')]
    alerts=[]
    for i,a in enumerate(meds):
        for b in meds[i+1:]:
            for pair,msg in pairs:
                if {a,b}==pair: alerts.append({'medicines':[a,b],'alert':msg})
    return jsonify(ok=True,alerts=alerts,notice='Demo rules only. No alert does not mean a combination is safe. Check all medicines, supplements, allergies, and doses with a pharmacist or clinician.')

@app.route('/api/ai/chat', methods=['POST'])
def chatbot():
    msg=payload().get('message','').strip().lower()
    if not msg: return jsonify(ok=False,error='Type a message.'),400
    if any(x in msg for x in ['emergency','chest pain','cannot breathe','can\'t breathe','suicid']): answer='This chatbot cannot handle emergencies. Contact local emergency services or go to the nearest emergency department now.'
    elif 'appointment' in msg: answer='To schedule an appointment, open Appointments, select a registered patient and available doctor, then choose a future date and time. The system blocks duplicate doctor time slots.'
    elif any(x in msg for x in ['lab','report','test result']): answer='Lab reports are managed in the Laboratory section. A report marked Pending is not complete; contact the clinical team for interpretation of a result.'
    elif any(x in msg for x in ['bill','billing','insurance']): answer='Bills are listed in Billing. Each bill totals consultation, laboratory, pharmacy and room charges. Insurance claim status is tracked separately.'
    elif any(x in msg for x in ['medicine','prescription','drug']): answer='Use the Pharmacy section to check inventory and the AI tools to view demo interaction checks or a plain-language reading aid. Always verify medicine decisions with a qualified pharmacist or clinician.'
    elif any(x in msg for x in ['patient','register']): answer='Open Patients and choose Register patient. A unique patient code is generated automatically. Only enter demo data in this prototype.'
    else: answer='I can help navigate patient registration, appointments, laboratory reports, pharmacy inventory, admissions, billing, and the demo AI tools. I cannot diagnose or replace clinical staff.'
    return jsonify(ok=True,answer=answer)

@app.route('/api/export')
def export_summary():
    return jsonify(ok=True,generated_at=datetime.utcnow().isoformat()+'Z',counts={'patients':Patient.query.count(),'doctors':Doctor.query.count(),'appointments':Appointment.query.count(),'admissions':Admission.query.count(),'lab_reports':LabReport.query.count(),'medicines':Medicine.query.count(),'bills':Bill.query.count()},note='Aggregate counts only; patient-level exports are intentionally not exposed in this demo.')

@app.route('/health')
def health():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify(status='ok', application='Smart Hospital Digital Ecosystem', database='connected'), 200
    except Exception:
        db.session.rollback()
        app.logger.exception('Database health check failed')
        return jsonify(status='error', application='Smart Hospital Digital Ecosystem', database='unavailable'), 503

@app.cli.command('init-db')
def init_db():
    """Create application tables in the configured database."""
    db.create_all()
    print('Database tables created in the configured database.')

@app.cli.command('seed-demo')
def seed_demo():
    """Seed demo records for local demonstration."""
    db.create_all()
    if Doctor.query.count()==0:
        db.session.add_all([Doctor(name='Dr. A. Meera',specialty='Cardiology',department='Cardiology',phone='9000000001'),Doctor(name='Dr. R. Karthik',specialty='General Medicine',department='Outpatient',phone='9000000002'),Doctor(name='Dr. N. Farah',specialty='Pediatrics',department='Pediatrics',phone='9000000003')])
    if Patient.query.count()==0:
        p1=Patient(patient_code='P-DEMO-001',name='Aarav Demo',dob='1998-03-12',gender='Male',phone='9000000101',email='aarav@example.test',blood_group='O+',allergies='None reported',emergency_contact='Demo contact',medical_history='demo record')
        p2=Patient(patient_code='P-DEMO-002',name='Diya Demo',dob='2002-07-20',gender='Female',phone='9000000102',email='diya@example.test',blood_group='A+',allergies='Not recorded',emergency_contact='Demo contact',medical_history='demo record')
        db.session.add_all([p1,p2]); db.session.flush()
        doc=Doctor.query.first()
        db.session.add(Appointment(patient_id=p1.id,doctor_id=doc.id,appointment_date=date.today().isoformat(),appointment_time='15:30',reason='Routine consultation'))
        db.session.add(LabReport(patient_id=p1.id,test_name='Complete blood count (demo)',sample_date=date.today().isoformat(),result='Pending',status='Pending',ordered_by=doc.name))
        db.session.add(Medicine(name='Demo paracetamol stock (not for dispensing)',category='Demo only',stock=8,reorder_level=10,unit_price=2.5,expiry_date='2027-12-31'))
        db.session.add(Bill(patient_id=p1.id,description='Demo consultation bill',consultation=500,laboratory=250,pharmacy=0,room=0,insurance_provider='Demo insurer',insurance_status='Not submitted'))
    db.session.commit(); print('Demo data seeded. Do not use as real patient data.')

if __name__ == '__main__':
    # Local SQLite convenience. On hosted deployments, run `flask --app app init-db`
    # explicitly instead of performing schema DDL on every request.
    if os.environ.get('AUTO_CREATE_TABLES', '1').lower() in ('1', 'true', 'yes'):
        with app.app_context():
            db.create_all()
    app.run(debug=os.environ.get('FLASK_DEBUG','0')=='1', host=os.environ.get('HOST', '127.0.0.1'), port=int(os.environ.get('PORT',5000)))
