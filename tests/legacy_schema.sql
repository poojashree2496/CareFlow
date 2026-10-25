CREATE TABLE admission (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	ward VARCHAR(80) NOT NULL, 
	bed VARCHAR(30), 
	admitted_on VARCHAR(10) NOT NULL, 
	discharged_on VARCHAR(10), 
	status VARCHAR(30), 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(patient_id) REFERENCES patient (id)
);
CREATE TABLE appointment (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	doctor_id INTEGER NOT NULL, 
	appointment_date VARCHAR(10) NOT NULL, 
	appointment_time VARCHAR(5) NOT NULL, 
	reason VARCHAR(300), 
	status VARCHAR(30), 
	PRIMARY KEY (id), 
	FOREIGN KEY(patient_id) REFERENCES patient (id), 
	FOREIGN KEY(doctor_id) REFERENCES doctor (id)
);
CREATE TABLE audit_log (
	id INTEGER NOT NULL, 
	action VARCHAR(120) NOT NULL, 
	details TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE bill (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	description VARCHAR(200) NOT NULL, 
	consultation FLOAT, 
	laboratory FLOAT, 
	pharmacy FLOAT, 
	room FLOAT, 
	insurance_provider VARCHAR(120), 
	insurance_status VARCHAR(40), 
	paid BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(patient_id) REFERENCES patient (id)
);
CREATE TABLE doctor (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	specialty VARCHAR(100) NOT NULL, 
	department VARCHAR(100), 
	phone VARCHAR(30), 
	available BOOLEAN, 
	PRIMARY KEY (id)
);
CREATE TABLE lab_report (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	test_name VARCHAR(120) NOT NULL, 
	sample_date VARCHAR(10) NOT NULL, 
	result TEXT, 
	status VARCHAR(30), 
	ordered_by VARCHAR(120), 
	PRIMARY KEY (id), 
	FOREIGN KEY(patient_id) REFERENCES patient (id)
);
CREATE TABLE medicine (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	category VARCHAR(80), 
	stock INTEGER, 
	reorder_level INTEGER, 
	unit_price FLOAT, 
	expiry_date VARCHAR(10), 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE patient (
	id INTEGER NOT NULL, 
	patient_code VARCHAR(20) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	dob VARCHAR(10), 
	gender VARCHAR(30), 
	phone VARCHAR(30), 
	email VARCHAR(120), 
	blood_group VARCHAR(5), 
	allergies TEXT, 
	emergency_contact VARCHAR(120), 
	medical_history TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (patient_code)
);
CREATE TABLE prescription (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	doctor_name VARCHAR(120), 
	medicine VARCHAR(120) NOT NULL, 
	dosage VARCHAR(120), 
	instructions TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(patient_id) REFERENCES patient (id)
);
CREATE TABLE radiology_record (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	modality VARCHAR(50) NOT NULL, 
	study_date VARCHAR(10) NOT NULL, 
	findings TEXT, 
	report_status VARCHAR(30), 
	PRIMARY KEY (id), 
	FOREIGN KEY(patient_id) REFERENCES patient (id)
);
