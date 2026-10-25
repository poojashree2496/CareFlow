import os
import pytest
from app import app, db, Patient, Doctor, Medicine

TEST_DB=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_hospital.db')

@pytest.fixture()
def client():
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI='sqlite:///' + TEST_DB)
    with app.app_context(): db.drop_all(); db.create_all()
    with app.test_client() as client: yield client
    with app.app_context(): db.session.remove(); db.drop_all()

def setup_patient_doctor(client):
    p=client.post('/api/patients',json={'name':'Test Patient'})
    assert p.status_code==200
    with app.app_context():
        patient=Patient.query.first(); db.session.add(Doctor(name='Dr Test',specialty='General')); db.session.commit(); return patient.id, Doctor.query.first().id

def test_health(client):
    r=client.get('/health'); assert r.status_code==200 and r.json['status']=='ok'

def test_patient_registration(client):
    r=client.post('/api/patients',json={'name':'Test Patient','phone':'123'}); assert r.status_code==200 and r.json['patient_code'].startswith('P-')

def test_patient_requires_name(client):
    assert client.post('/api/patients',json={}).status_code==400

def test_appointment_conflict(client):
    pid,did=setup_patient_doctor(client); data={'patient_id':pid,'doctor_id':did,'appointment_date':'2099-01-01','appointment_time':'10:00'}
    assert client.post('/api/appointments',json=data).status_code==200
    assert client.post('/api/appointments',json=data).status_code==400

def test_negative_stock_rejected(client):
    client.post('/api/medicines',json={'name':'Demo','stock':2})
    with app.app_context(): mid=Medicine.query.first().id
    assert client.patch(f'/api/medicines/{mid}',json={'stock':-1}).status_code==400

def test_ai_disclaimer(client):
    r=client.post('/api/ai/disease-prediction',json={'symptoms':'fever, cough'}); assert r.status_code==200 and 'not a diagnosis' in r.json['notice'].lower()
