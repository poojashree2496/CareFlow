-- CareFlow database schema.
-- Generated from the application models (careflow/models.py). The migrations in migrations/versions create exactly this schema.
-- 48 tables.

-- ---- department
CREATE TABLE department (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_department PRIMARY KEY (id), 
	CONSTRAINT uq_department_name UNIQUE (name)
);


-- ---- doctor
CREATE TABLE doctor (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	specialty VARCHAR(100) NOT NULL, 
	department VARCHAR(100), 
	phone VARCHAR(30), 
	available BOOLEAN, 
	registration_no VARCHAR(60), 
	CONSTRAINT pk_doctor PRIMARY KEY (id)
);


-- ---- medicine
CREATE TABLE medicine (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	category VARCHAR(80), 
	stock INTEGER, 
	reorder_level INTEGER, 
	unit_price FLOAT, 
	expiry_date VARCHAR(10), 
	generic_name VARCHAR(120), 
	strength VARCHAR(40), 
	form VARCHAR(40), 
	batch_no VARCHAR(40), 
	is_active BOOLEAN, 
	CONSTRAINT pk_medicine PRIMARY KEY (id), 
	CONSTRAINT ck_medicine_stock_nonneg CHECK (stock >= 0), 
	CONSTRAINT uq_medicine_name UNIQUE (name)
);


-- ---- observation_type
CREATE TABLE observation_type (
	code VARCHAR(30) NOT NULL, 
	label VARCHAR(80) NOT NULL, 
	unit VARCHAR(20) NOT NULL, 
	plausible_min FLOAT, 
	plausible_max FLOAT, 
	decimals INTEGER, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_observation_type PRIMARY KEY (code)
);


-- ---- ward
CREATE TABLE ward (
	id INTEGER NOT NULL, 
	name VARCHAR(80) NOT NULL, 
	department_id INTEGER, 
	specialty VARCHAR(100), 
	floor VARCHAR(20), 
	daily_rate FLOAT NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_ward PRIMARY KEY (id), 
	CONSTRAINT uq_ward_name UNIQUE (name), 
	CONSTRAINT fk_ward_department_id_department FOREIGN KEY(department_id) REFERENCES department (id)
);


-- ---- app_user
CREATE TABLE app_user (
	id INTEGER NOT NULL, 
	email VARCHAR(200) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(300) NOT NULL, 
	role VARCHAR(30) NOT NULL, 
	doctor_id INTEGER, 
	ward_id INTEGER, 
	patient_id INTEGER, 
	is_active BOOLEAN NOT NULL, 
	is_demo BOOLEAN NOT NULL, 
	must_change_password BOOLEAN NOT NULL, 
	failed_logins INTEGER NOT NULL, 
	locked_until DATETIME, 
	last_login_at DATETIME, 
	password_changed_at DATETIME, 
	session_epoch INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	created_by_id INTEGER, 
	CONSTRAINT pk_app_user PRIMARY KEY (id), 
	CONSTRAINT ck_app_user_role_valid CHECK (role IN ('super_admin','hospital_admin','doctor','nurse','lab_staff','pharmacist','radiology_staff','billing_staff','patient')), 
	CONSTRAINT ck_app_user_patient_link_matches_role CHECK ((role = 'patient') = (patient_id IS NOT NULL)), 
	CONSTRAINT uq_app_user_email UNIQUE (email), 
	CONSTRAINT uq_app_user_doctor_id UNIQUE (doctor_id), 
	CONSTRAINT fk_app_user_doctor_id_doctor FOREIGN KEY(doctor_id) REFERENCES doctor (id), 
	CONSTRAINT fk_app_user_ward_id_ward FOREIGN KEY(ward_id) REFERENCES ward (id), 
	CONSTRAINT uq_app_user_patient_id UNIQUE (patient_id), 
	CONSTRAINT fk_app_user_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_app_user_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_app_user_role ON app_user (role);

-- ---- room
CREATE TABLE room (
	id INTEGER NOT NULL, 
	ward_id INTEGER NOT NULL, 
	label VARCHAR(30) NOT NULL, 
	CONSTRAINT pk_room PRIMARY KEY (id), 
	CONSTRAINT uq_room_ward_label UNIQUE (ward_id, label), 
	CONSTRAINT fk_room_ward_id_ward FOREIGN KEY(ward_id) REFERENCES ward (id)
);

CREATE INDEX ix_room_ward_id ON room (ward_id);

-- ---- alert_rule
CREATE TABLE alert_rule (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	description VARCHAR(300), 
	rule_kind VARCHAR(12) NOT NULL, 
	type_code VARCHAR(30), 
	operator VARCHAR(3), 
	threshold FLOAT, 
	severity VARCHAR(10) NOT NULL, 
	window_minutes INTEGER, 
	cooldown_minutes INTEGER, 
	active BOOLEAN NOT NULL, 
	version INTEGER NOT NULL, 
	review_status VARCHAR(12) NOT NULL, 
	reviewed_by VARCHAR(120), 
	reviewed_at DATETIME, 
	created_by_id INTEGER, 
	updated_at DATETIME, 
	CONSTRAINT pk_alert_rule PRIMARY KEY (id), 
	CONSTRAINT ck_alert_rule_kind_valid CHECK (rule_kind IN ('threshold','missing')), 
	CONSTRAINT ck_alert_rule_severity_valid CHECK (severity IN ('Info','Warning','Critical')), 
	CONSTRAINT fk_alert_rule_type_code_observation_type FOREIGN KEY(type_code) REFERENCES observation_type (code), 
	CONSTRAINT fk_alert_rule_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);


-- ---- bed
CREATE TABLE bed (
	id INTEGER NOT NULL, 
	room_id INTEGER NOT NULL, 
	ward_id INTEGER NOT NULL, 
	label VARCHAR(30) NOT NULL, 
	code VARCHAR(40) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	status_note VARCHAR(200), 
	status_changed_at DATETIME, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_bed PRIMARY KEY (id), 
	CONSTRAINT ck_bed_status_valid CHECK (status IN ('Available','Occupied','Cleaning','Reserved','Maintenance')), 
	CONSTRAINT uq_bed_room_label UNIQUE (room_id, label), 
	CONSTRAINT fk_bed_room_id_room FOREIGN KEY(room_id) REFERENCES room (id), 
	CONSTRAINT fk_bed_ward_id_ward FOREIGN KEY(ward_id) REFERENCES ward (id), 
	CONSTRAINT uq_bed_code UNIQUE (code)
);

CREATE INDEX ix_bed_room_id ON bed (room_id);
CREATE INDEX ix_bed_ward_id ON bed (ward_id);

-- ---- patient
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
	created_at DATETIME NOT NULL, 
	address TEXT, 
	emergency_contact_phone VARCHAR(30), 
	emergency_contact_relation VARCHAR(60), 
	identifier_label VARCHAR(60), 
	identifier_last4 VARCHAR(4), 
	identity_verified BOOLEAN, 
	identity_verified_by_id INTEGER, 
	identity_verified_at DATETIME, 
	consent_data_sharing BOOLEAN, 
	consent_notes TEXT, 
	insurance_provider VARCHAR(120), 
	insurance_policy_no VARCHAR(60), 
	data_origin VARCHAR(20), 
	archived_at DATETIME, 
	updated_at DATETIME, 
	CONSTRAINT pk_patient PRIMARY KEY (id), 
	CONSTRAINT uq_patient_patient_code UNIQUE (patient_code), 
	CONSTRAINT fk_patient_identity_verified_by_id_app_user FOREIGN KEY(identity_verified_by_id) REFERENCES app_user (id)
);


-- ---- stock_movement
CREATE TABLE stock_movement (
	id INTEGER NOT NULL, 
	medicine_id INTEGER NOT NULL, 
	delta INTEGER NOT NULL, 
	balance_after INTEGER NOT NULL, 
	reason VARCHAR(30) NOT NULL, 
	ref_type VARCHAR(30), 
	ref_id INTEGER, 
	user_id INTEGER, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_stock_movement PRIMARY KEY (id), 
	CONSTRAINT fk_stock_movement_medicine_id_medicine FOREIGN KEY(medicine_id) REFERENCES medicine (id), 
	CONSTRAINT fk_stock_movement_user_id_app_user FOREIGN KEY(user_id) REFERENCES app_user (id)
);

CREATE INDEX ix_stock_movement_medicine_id ON stock_movement (medicine_id);

-- ---- system_setting
CREATE TABLE system_setting (
	"key" VARCHAR(80) NOT NULL, 
	value JSON, 
	updated_by_id INTEGER, 
	updated_at DATETIME, 
	CONSTRAINT pk_system_setting PRIMARY KEY ("key"), 
	CONSTRAINT fk_system_setting_updated_by_id_app_user FOREIGN KEY(updated_by_id) REFERENCES app_user (id)
);


-- ---- ai_conversation
CREATE TABLE ai_conversation (
	id VARCHAR(36) NOT NULL, 
	user_id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	title VARCHAR(200), 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	deleted_at DATETIME, 
	CONSTRAINT pk_ai_conversation PRIMARY KEY (id), 
	CONSTRAINT fk_ai_conversation_user_id_app_user FOREIGN KEY(user_id) REFERENCES app_user (id), 
	CONSTRAINT fk_ai_conversation_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id)
);

CREATE INDEX ix_ai_conversation_patient_id ON ai_conversation (patient_id);
CREATE INDEX ix_ai_conversation_user_id ON ai_conversation (user_id);

-- ---- allergy
CREATE TABLE allergy (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	substance VARCHAR(120) NOT NULL, 
	reaction VARCHAR(200), 
	severity VARCHAR(20), 
	status VARCHAR(20) NOT NULL, 
	recorded_by_id INTEGER, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_allergy PRIMARY KEY (id), 
	CONSTRAINT fk_allergy_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_allergy_recorded_by_id_app_user FOREIGN KEY(recorded_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_allergy_patient_id ON allergy (patient_id);

-- ---- appointment
CREATE TABLE appointment (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	doctor_id INTEGER NOT NULL, 
	appointment_date VARCHAR(10) NOT NULL, 
	appointment_time VARCHAR(5) NOT NULL, 
	reason VARCHAR(300), 
	status VARCHAR(30), 
	duration_min INTEGER, 
	visit_type VARCHAR(30), 
	cancel_reason VARCHAR(200), 
	reschedule_count INTEGER, 
	created_by_id INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	CONSTRAINT pk_appointment PRIMARY KEY (id), 
	CONSTRAINT fk_appointment_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_appointment_doctor_id_doctor FOREIGN KEY(doctor_id) REFERENCES doctor (id), 
	CONSTRAINT fk_appointment_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_appointment_doctor_day ON appointment (doctor_id, appointment_date);
CREATE INDEX ix_appointment_patient ON appointment (patient_id);
CREATE UNIQUE INDEX uq_appointment_doctor_slot_active ON appointment (doctor_id, appointment_date, appointment_time) WHERE status IN ('Scheduled','Checked-in');

-- ---- audit_log
CREATE TABLE audit_log (
	id INTEGER NOT NULL, 
	action VARCHAR(120) NOT NULL, 
	details TEXT, 
	created_at DATETIME NOT NULL, 
	user_id INTEGER, 
	user_role VARCHAR(30), 
	category VARCHAR(16), 
	entity_type VARCHAR(40), 
	entity_id INTEGER, 
	patient_id INTEGER, 
	outcome VARCHAR(10), 
	ip VARCHAR(64), 
	request_id VARCHAR(36), 
	CONSTRAINT pk_audit_log PRIMARY KEY (id), 
	CONSTRAINT fk_audit_log_user_id_app_user FOREIGN KEY(user_id) REFERENCES app_user (id), 
	CONSTRAINT fk_audit_log_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id)
);

CREATE INDEX ix_audit_log_created ON audit_log (created_at);
CREATE INDEX ix_audit_log_patient ON audit_log (patient_id);

-- ---- critical_ack
CREATE TABLE critical_ack (
	id INTEGER NOT NULL, 
	source_type VARCHAR(12) NOT NULL, 
	source_id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	summary VARCHAR(300), 
	notify_user_id INTEGER, 
	status VARCHAR(12) NOT NULL, 
	created_at DATETIME NOT NULL, 
	ack_by_id INTEGER, 
	ack_at DATETIME, 
	ack_note VARCHAR(300), 
	escalated_at DATETIME, 
	escalated_to_role VARCHAR(30), 
	CONSTRAINT pk_critical_ack PRIMARY KEY (id), 
	CONSTRAINT uq_critical_ack_source UNIQUE (source_type, source_id), 
	CONSTRAINT ck_critical_ack_status_valid CHECK (status IN ('Pending','Acknowledged','Escalated')), 
	CONSTRAINT fk_critical_ack_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_critical_ack_notify_user_id_app_user FOREIGN KEY(notify_user_id) REFERENCES app_user (id), 
	CONSTRAINT fk_critical_ack_ack_by_id_app_user FOREIGN KEY(ack_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_critical_ack_patient_id ON critical_ack (patient_id);

-- ---- monitoring_device
CREATE TABLE monitoring_device (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	kind VARCHAR(60), 
	patient_id INTEGER, 
	is_simulated BOOLEAN NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	api_key_hash VARCHAR(128), 
	api_key_prefix VARCHAR(12), 
	last_seen_at DATETIME, 
	created_by_id INTEGER, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_monitoring_device PRIMARY KEY (id), 
	CONSTRAINT fk_monitoring_device_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_monitoring_device_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_monitoring_device_patient_id ON monitoring_device (patient_id);

-- ---- notification
CREATE TABLE notification (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	role VARCHAR(30), 
	kind VARCHAR(40) NOT NULL, 
	severity VARCHAR(10), 
	title VARCHAR(200) NOT NULL, 
	body VARCHAR(400), 
	patient_id INTEGER, 
	ref_type VARCHAR(30), 
	ref_id INTEGER, 
	delivery VARCHAR(12), 
	created_at DATETIME NOT NULL, 
	read_at DATETIME, 
	CONSTRAINT pk_notification PRIMARY KEY (id), 
	CONSTRAINT fk_notification_user_id_app_user FOREIGN KEY(user_id) REFERENCES app_user (id), 
	CONSTRAINT fk_notification_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id)
);

CREATE INDEX ix_notification_role ON notification (role);
CREATE INDEX ix_notification_user_id ON notification (user_id);

-- ---- patient_assignment
CREATE TABLE patient_assignment (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	relation VARCHAR(20) NOT NULL, 
	active BOOLEAN NOT NULL, 
	starts_at DATETIME, 
	ends_at DATETIME, 
	created_by_id INTEGER, 
	CONSTRAINT pk_patient_assignment PRIMARY KEY (id), 
	CONSTRAINT fk_patient_assignment_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_patient_assignment_user_id_app_user FOREIGN KEY(user_id) REFERENCES app_user (id), 
	CONSTRAINT fk_patient_assignment_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_patient_assignment_patient_id ON patient_assignment (patient_id);
CREATE INDEX ix_patient_assignment_user_id ON patient_assignment (user_id);
CREATE UNIQUE INDEX uq_patient_assignment_active ON patient_assignment (patient_id, user_id) WHERE active = 1;

-- ---- ai_message
CREATE TABLE ai_message (
	id INTEGER NOT NULL, 
	conversation_id VARCHAR(36) NOT NULL, 
	role VARCHAR(10) NOT NULL, 
	content TEXT NOT NULL, 
	mode VARCHAR(12), 
	status VARCHAR(24), 
	sources JSON, 
	limitations JSON, 
	provider VARCHAR(30), 
	model VARCHAR(60), 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_ai_message PRIMARY KEY (id), 
	CONSTRAINT fk_ai_message_conversation_id_ai_conversation FOREIGN KEY(conversation_id) REFERENCES ai_conversation (id)
);

CREATE INDEX ix_ai_message_conversation_id ON ai_message (conversation_id);

-- ---- encounter
CREATE TABLE encounter (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	encounter_type VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	doctor_id INTEGER, 
	appointment_id INTEGER, 
	chief_complaint VARCHAR(300), 
	started_at DATETIME, 
	ended_at DATETIME, 
	created_by_id INTEGER, 
	CONSTRAINT pk_encounter PRIMARY KEY (id), 
	CONSTRAINT fk_encounter_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_encounter_doctor_id_doctor FOREIGN KEY(doctor_id) REFERENCES doctor (id), 
	CONSTRAINT fk_encounter_appointment_id_appointment FOREIGN KEY(appointment_id) REFERENCES appointment (id), 
	CONSTRAINT fk_encounter_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_encounter_patient_id ON encounter (patient_id);

-- ---- admission
CREATE TABLE admission (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	ward VARCHAR(80) NOT NULL, 
	bed VARCHAR(30), 
	admitted_on VARCHAR(10) NOT NULL, 
	discharged_on VARCHAR(10), 
	status VARCHAR(30), 
	notes TEXT, 
	encounter_id INTEGER, 
	responsible_doctor_id INTEGER, 
	admitted_at DATETIME, 
	discharged_at DATETIME, 
	expected_discharge_on VARCHAR(10), 
	reason TEXT, 
	discharge_status VARCHAR(20), 
	discharge_plan TEXT, 
	discharge_summary TEXT, 
	discharge_authorized_by_id INTEGER, 
	discharge_authorized_at DATETIME, 
	created_by_id INTEGER, 
	CONSTRAINT pk_admission PRIMARY KEY (id), 
	CONSTRAINT fk_admission_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_admission_encounter_id_encounter FOREIGN KEY(encounter_id) REFERENCES encounter (id), 
	CONSTRAINT fk_admission_responsible_doctor_id_doctor FOREIGN KEY(responsible_doctor_id) REFERENCES doctor (id), 
	CONSTRAINT fk_admission_discharge_authorized_by_id_app_user FOREIGN KEY(discharge_authorized_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_admission_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);

CREATE UNIQUE INDEX uq_admission_active_patient ON admission (patient_id) WHERE status = 'Admitted';

-- ---- problem
CREATE TABLE problem (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	encounter_id INTEGER, 
	description VARCHAR(300) NOT NULL, 
	code VARCHAR(30), 
	status VARCHAR(20) NOT NULL, 
	onset_on VARCHAR(10), 
	recorded_by_id INTEGER, 
	created_at DATETIME NOT NULL, 
	resolved_at DATETIME, 
	CONSTRAINT pk_problem PRIMARY KEY (id), 
	CONSTRAINT fk_problem_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_problem_encounter_id_encounter FOREIGN KEY(encounter_id) REFERENCES encounter (id), 
	CONSTRAINT fk_problem_recorded_by_id_app_user FOREIGN KEY(recorded_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_problem_patient_id ON problem (patient_id);

-- ---- bed_assignment
CREATE TABLE bed_assignment (
	id INTEGER NOT NULL, 
	admission_id INTEGER NOT NULL, 
	bed_id INTEGER NOT NULL, 
	started_at DATETIME NOT NULL, 
	ended_at DATETIME, 
	reason VARCHAR(30), 
	end_reason VARCHAR(30), 
	moved_by_id INTEGER, 
	note VARCHAR(300), 
	CONSTRAINT pk_bed_assignment PRIMARY KEY (id), 
	CONSTRAINT fk_bed_assignment_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_bed_assignment_bed_id_bed FOREIGN KEY(bed_id) REFERENCES bed (id), 
	CONSTRAINT fk_bed_assignment_moved_by_id_app_user FOREIGN KEY(moved_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_bed_assignment_admission_id ON bed_assignment (admission_id);
CREATE INDEX ix_bed_assignment_bed_id ON bed_assignment (bed_id);
CREATE UNIQUE INDEX uq_bed_assignment_open_admission ON bed_assignment (admission_id) WHERE ended_at IS NULL;
CREATE UNIQUE INDEX uq_bed_assignment_open_bed ON bed_assignment (bed_id) WHERE ended_at IS NULL;

-- ---- bill
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
	created_at DATETIME NOT NULL, 
	other_charges FLOAT, 
	encounter_id INTEGER, 
	admission_id INTEGER, 
	status VARCHAR(12), 
	created_by_id INTEGER, 
	voided_at DATETIME, 
	CONSTRAINT pk_bill PRIMARY KEY (id), 
	CONSTRAINT fk_bill_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_bill_encounter_id_encounter FOREIGN KEY(encounter_id) REFERENCES encounter (id), 
	CONSTRAINT fk_bill_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_bill_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);


-- ---- care_plan
CREATE TABLE care_plan (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	admission_id INTEGER, 
	title VARCHAR(200) NOT NULL, 
	goals TEXT, 
	status VARCHAR(20) NOT NULL, 
	author_id INTEGER, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_care_plan PRIMARY KEY (id), 
	CONSTRAINT fk_care_plan_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_care_plan_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_care_plan_author_id_app_user FOREIGN KEY(author_id) REFERENCES app_user (id)
);

CREATE INDEX ix_care_plan_patient_id ON care_plan (patient_id);

-- ---- clinical_note
CREATE TABLE clinical_note (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	encounter_id INTEGER, 
	admission_id INTEGER, 
	author_id INTEGER NOT NULL, 
	note_type VARCHAR(30) NOT NULL, 
	body TEXT NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	amends_note_id INTEGER, 
	amendment_reason VARCHAR(300), 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_clinical_note PRIMARY KEY (id), 
	CONSTRAINT ck_clinical_note_status_valid CHECK (status IN ('Final','Superseded')), 
	CONSTRAINT fk_clinical_note_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_clinical_note_encounter_id_encounter FOREIGN KEY(encounter_id) REFERENCES encounter (id), 
	CONSTRAINT fk_clinical_note_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_clinical_note_author_id_app_user FOREIGN KEY(author_id) REFERENCES app_user (id), 
	CONSTRAINT fk_clinical_note_amends_note_id_clinical_note FOREIGN KEY(amends_note_id) REFERENCES clinical_note (id)
);

CREATE INDEX ix_clinical_note_patient_id ON clinical_note (patient_id);

-- ---- follow_up
CREATE TABLE follow_up (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	encounter_id INTEGER, 
	admission_id INTEGER, 
	due_on VARCHAR(10), 
	instructions TEXT, 
	appointment_id INTEGER, 
	status VARCHAR(20) NOT NULL, 
	created_by_id INTEGER, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_follow_up PRIMARY KEY (id), 
	CONSTRAINT fk_follow_up_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_follow_up_encounter_id_encounter FOREIGN KEY(encounter_id) REFERENCES encounter (id), 
	CONSTRAINT fk_follow_up_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_follow_up_appointment_id_appointment FOREIGN KEY(appointment_id) REFERENCES appointment (id), 
	CONSTRAINT fk_follow_up_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_follow_up_patient_id ON follow_up (patient_id);

-- ---- handover
CREATE TABLE handover (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	admission_id INTEGER, 
	ward_id INTEGER, 
	kind VARCHAR(20) NOT NULL, 
	shift VARCHAR(20), 
	situation TEXT, 
	background TEXT, 
	assessment TEXT, 
	recommendation TEXT, 
	is_auto_draft BOOLEAN NOT NULL, 
	author_id INTEGER, 
	reviewed_by_id INTEGER, 
	reviewed_at DATETIME, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_handover PRIMARY KEY (id), 
	CONSTRAINT fk_handover_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_handover_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_handover_ward_id_ward FOREIGN KEY(ward_id) REFERENCES ward (id), 
	CONSTRAINT fk_handover_author_id_app_user FOREIGN KEY(author_id) REFERENCES app_user (id), 
	CONSTRAINT fk_handover_reviewed_by_id_app_user FOREIGN KEY(reviewed_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_handover_patient_id ON handover (patient_id);

-- ---- intake_output
CREATE TABLE intake_output (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	admission_id INTEGER, 
	kind VARCHAR(10) NOT NULL, 
	item VARCHAR(100), 
	amount_ml FLOAT NOT NULL, 
	recorded_by_id INTEGER, 
	recorded_at DATETIME NOT NULL, 
	CONSTRAINT pk_intake_output PRIMARY KEY (id), 
	CONSTRAINT ck_intake_output_kind_valid CHECK (kind IN ('Intake','Output')), 
	CONSTRAINT ck_intake_output_amount_nonneg CHECK (amount_ml >= 0), 
	CONSTRAINT fk_intake_output_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_intake_output_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_intake_output_recorded_by_id_app_user FOREIGN KEY(recorded_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_intake_output_patient_id ON intake_output (patient_id);

-- ---- lab_report
CREATE TABLE lab_report (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	test_name VARCHAR(120) NOT NULL, 
	sample_date VARCHAR(10) NOT NULL, 
	result TEXT, 
	status VARCHAR(30), 
	ordered_by VARCHAR(120), 
	encounter_id INTEGER, 
	admission_id INTEGER, 
	ordered_by_id INTEGER, 
	accession_no VARCHAR(30), 
	priority VARCHAR(10), 
	specimen_type VARCHAR(60), 
	clinical_info VARCHAR(300), 
	ordered_at DATETIME, 
	collected_at DATETIME, 
	collected_by_id INTEGER, 
	received_at DATETIME, 
	resulted_at DATETIME, 
	resulted_by_id INTEGER, 
	verified_at DATETIME, 
	verified_by_id INTEGER, 
	released_at DATETIME, 
	released_by_id INTEGER, 
	rejected_at DATETIME, 
	rejected_reason VARCHAR(300), 
	amendment_count INTEGER, 
	CONSTRAINT pk_lab_report PRIMARY KEY (id), 
	CONSTRAINT fk_lab_report_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_lab_report_encounter_id_encounter FOREIGN KEY(encounter_id) REFERENCES encounter (id), 
	CONSTRAINT fk_lab_report_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_lab_report_ordered_by_id_app_user FOREIGN KEY(ordered_by_id) REFERENCES app_user (id), 
	CONSTRAINT uq_lab_report_accession_no UNIQUE (accession_no), 
	CONSTRAINT fk_lab_report_collected_by_id_app_user FOREIGN KEY(collected_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_lab_report_resulted_by_id_app_user FOREIGN KEY(resulted_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_lab_report_verified_by_id_app_user FOREIGN KEY(verified_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_lab_report_released_by_id_app_user FOREIGN KEY(released_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_lab_report_patient_status ON lab_report (patient_id, status);

-- ---- med_reconciliation
CREATE TABLE med_reconciliation (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	admission_id INTEGER, 
	pharmacist_id INTEGER, 
	items JSON, 
	notes TEXT, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_med_reconciliation PRIMARY KEY (id), 
	CONSTRAINT fk_med_reconciliation_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_med_reconciliation_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_med_reconciliation_pharmacist_id_app_user FOREIGN KEY(pharmacist_id) REFERENCES app_user (id)
);

CREATE INDEX ix_med_reconciliation_patient_id ON med_reconciliation (patient_id);

-- ---- observation
CREATE TABLE observation (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	admission_id INTEGER, 
	encounter_id INTEGER, 
	type_code VARCHAR(30) NOT NULL, 
	value_num FLOAT NOT NULL, 
	unit VARCHAR(20) NOT NULL, 
	observed_at DATETIME NOT NULL, 
	recorded_at DATETIME NOT NULL, 
	source VARCHAR(12) NOT NULL, 
	device_id INTEGER, 
	recorded_by_id INTEGER, 
	validation_status VARCHAR(20) NOT NULL, 
	supersedes_id INTEGER, 
	correction_reason VARCHAR(300), 
	group_id VARCHAR(36), 
	note VARCHAR(300), 
	CONSTRAINT pk_observation PRIMARY KEY (id), 
	CONSTRAINT ck_observation_source_valid CHECK (source IN ('manual','device','simulated')), 
	CONSTRAINT ck_observation_validation_valid CHECK (validation_status IN ('Valid','Unverified','Corrected','Entered in error')), 
	CONSTRAINT fk_observation_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_observation_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_observation_encounter_id_encounter FOREIGN KEY(encounter_id) REFERENCES encounter (id), 
	CONSTRAINT fk_observation_type_code_observation_type FOREIGN KEY(type_code) REFERENCES observation_type (code), 
	CONSTRAINT fk_observation_device_id_monitoring_device FOREIGN KEY(device_id) REFERENCES monitoring_device (id), 
	CONSTRAINT fk_observation_recorded_by_id_app_user FOREIGN KEY(recorded_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_observation_supersedes_id_observation FOREIGN KEY(supersedes_id) REFERENCES observation (id)
);

CREATE INDEX ix_observation_patient_type_time ON observation (patient_id, type_code, observed_at);

-- ---- prescription
CREATE TABLE prescription (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	doctor_name VARCHAR(120), 
	medicine VARCHAR(120) NOT NULL, 
	dosage VARCHAR(120), 
	instructions TEXT, 
	created_at DATETIME NOT NULL, 
	ordered_by_id INTEGER, 
	encounter_id INTEGER, 
	admission_id INTEGER, 
	medicine_id INTEGER, 
	route VARCHAR(30), 
	frequency VARCHAR(60), 
	duration_days INTEGER, 
	quantity INTEGER, 
	is_prn BOOLEAN, 
	status VARCHAR(24), 
	allergy_override_reason VARCHAR(300), 
	warnings JSON, 
	verified_by_id INTEGER, 
	verified_at DATETIME, 
	cancelled_reason VARCHAR(300), 
	dispensed_quantity INTEGER, 
	CONSTRAINT pk_prescription PRIMARY KEY (id), 
	CONSTRAINT fk_prescription_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_prescription_ordered_by_id_app_user FOREIGN KEY(ordered_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_prescription_encounter_id_encounter FOREIGN KEY(encounter_id) REFERENCES encounter (id), 
	CONSTRAINT fk_prescription_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_prescription_medicine_id_medicine FOREIGN KEY(medicine_id) REFERENCES medicine (id), 
	CONSTRAINT fk_prescription_verified_by_id_app_user FOREIGN KEY(verified_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_prescription_patient_status ON prescription (patient_id, status);

-- ---- radiology_record
CREATE TABLE radiology_record (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	modality VARCHAR(50) NOT NULL, 
	study_date VARCHAR(10) NOT NULL, 
	findings TEXT, 
	report_status VARCHAR(30), 
	encounter_id INTEGER, 
	admission_id INTEGER, 
	ordered_by_id INTEGER, 
	order_status VARCHAR(12), 
	study_description VARCHAR(200), 
	indication VARCHAR(300), 
	priority VARCHAR(10), 
	scheduled_at DATETIME, 
	performed_at DATETIME, 
	performed_by_id INTEGER, 
	impression TEXT, 
	recommendations TEXT, 
	reported_by_id INTEGER, 
	reported_at DATETIME, 
	authorized_by_id INTEGER, 
	authorized_at DATETIME, 
	urgent_finding BOOLEAN, 
	amendment_count INTEGER, 
	ordered_at DATETIME, 
	CONSTRAINT pk_radiology_record PRIMARY KEY (id), 
	CONSTRAINT fk_radiology_record_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_radiology_record_encounter_id_encounter FOREIGN KEY(encounter_id) REFERENCES encounter (id), 
	CONSTRAINT fk_radiology_record_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_radiology_record_ordered_by_id_app_user FOREIGN KEY(ordered_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_radiology_record_performed_by_id_app_user FOREIGN KEY(performed_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_radiology_record_reported_by_id_app_user FOREIGN KEY(reported_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_radiology_record_authorized_by_id_app_user FOREIGN KEY(authorized_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_radiology_patient ON radiology_record (patient_id);

-- ---- alert
CREATE TABLE alert (
	id INTEGER NOT NULL, 
	rule_id INTEGER NOT NULL, 
	rule_version INTEGER NOT NULL, 
	rule_snapshot JSON, 
	patient_id INTEGER NOT NULL, 
	admission_id INTEGER, 
	observation_id INTEGER, 
	severity VARCHAR(10) NOT NULL, 
	status VARCHAR(12) NOT NULL, 
	message VARCHAR(300), 
	triggered_at DATETIME NOT NULL, 
	last_triggered_at DATETIME, 
	occurrences INTEGER NOT NULL, 
	from_simulated_data BOOLEAN NOT NULL, 
	responder_user_id INTEGER, 
	responder_role VARCHAR(30), 
	ack_by_id INTEGER, 
	ack_at DATETIME, 
	escalated_at DATETIME, 
	escalated_to_role VARCHAR(30), 
	resolved_by_id INTEGER, 
	resolved_at DATETIME, 
	resolution_note VARCHAR(300), 
	CONSTRAINT pk_alert PRIMARY KEY (id), 
	CONSTRAINT ck_alert_status_valid CHECK (status IN ('Open','Acknowledged','Escalated','Resolved')), 
	CONSTRAINT fk_alert_rule_id_alert_rule FOREIGN KEY(rule_id) REFERENCES alert_rule (id), 
	CONSTRAINT fk_alert_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_alert_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_alert_observation_id_observation FOREIGN KEY(observation_id) REFERENCES observation (id), 
	CONSTRAINT fk_alert_responder_user_id_app_user FOREIGN KEY(responder_user_id) REFERENCES app_user (id), 
	CONSTRAINT fk_alert_ack_by_id_app_user FOREIGN KEY(ack_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_alert_resolved_by_id_app_user FOREIGN KEY(resolved_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_alert_patient_id ON alert (patient_id);
CREATE UNIQUE INDEX uq_alert_open_patient_rule ON alert (patient_id, rule_id) WHERE status <> 'Resolved';

-- ---- bill_adjustment
CREATE TABLE bill_adjustment (
	id INTEGER NOT NULL, 
	bill_id INTEGER NOT NULL, 
	kind VARCHAR(20) NOT NULL, 
	amount FLOAT NOT NULL, 
	reason VARCHAR(300) NOT NULL, 
	requested_by_id INTEGER, 
	approved_by_id INTEGER, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_bill_adjustment PRIMARY KEY (id), 
	CONSTRAINT ck_bill_adjustment_amount_positive CHECK (amount > 0), 
	CONSTRAINT fk_bill_adjustment_bill_id_bill FOREIGN KEY(bill_id) REFERENCES bill (id), 
	CONSTRAINT fk_bill_adjustment_requested_by_id_app_user FOREIGN KEY(requested_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_bill_adjustment_approved_by_id_app_user FOREIGN KEY(approved_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_bill_adjustment_bill_id ON bill_adjustment (bill_id);

-- ---- care_task
CREATE TABLE care_task (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	admission_id INTEGER, 
	care_plan_id INTEGER, 
	title VARCHAR(200) NOT NULL, 
	category VARCHAR(30) NOT NULL, 
	assigned_role VARCHAR(30), 
	assigned_user_id INTEGER, 
	due_at DATETIME, 
	status VARCHAR(20) NOT NULL, 
	priority VARCHAR(20) NOT NULL, 
	notes TEXT, 
	completed_at DATETIME, 
	completed_by_id INTEGER, 
	created_by_id INTEGER, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_care_task PRIMARY KEY (id), 
	CONSTRAINT ck_care_task_status_valid CHECK (status IN ('Pending','Done','Cancelled')), 
	CONSTRAINT fk_care_task_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_care_task_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_care_task_care_plan_id_care_plan FOREIGN KEY(care_plan_id) REFERENCES care_plan (id), 
	CONSTRAINT fk_care_task_assigned_user_id_app_user FOREIGN KEY(assigned_user_id) REFERENCES app_user (id), 
	CONSTRAINT fk_care_task_completed_by_id_app_user FOREIGN KEY(completed_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_care_task_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_care_task_admission_id ON care_task (admission_id);
CREATE INDEX ix_care_task_due_at ON care_task (due_at);
CREATE INDEX ix_care_task_patient_id ON care_task (patient_id);

-- ---- dispense_event
CREATE TABLE dispense_event (
	id INTEGER NOT NULL, 
	prescription_id INTEGER NOT NULL, 
	medicine_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	dispensed_by_id INTEGER NOT NULL, 
	dispensed_at DATETIME NOT NULL, 
	warnings_acknowledged JSON, 
	note VARCHAR(300), 
	CONSTRAINT pk_dispense_event PRIMARY KEY (id), 
	CONSTRAINT ck_dispense_event_qty_positive CHECK (quantity > 0), 
	CONSTRAINT fk_dispense_event_prescription_id_prescription FOREIGN KEY(prescription_id) REFERENCES prescription (id), 
	CONSTRAINT fk_dispense_event_medicine_id_medicine FOREIGN KEY(medicine_id) REFERENCES medicine (id), 
	CONSTRAINT fk_dispense_event_dispensed_by_id_app_user FOREIGN KEY(dispensed_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_dispense_event_prescription_id ON dispense_event (prescription_id);

-- ---- insurance_claim
CREATE TABLE insurance_claim (
	id INTEGER NOT NULL, 
	bill_id INTEGER NOT NULL, 
	provider VARCHAR(120) NOT NULL, 
	policy_no VARCHAR(60), 
	claim_no VARCHAR(60), 
	amount_claimed FLOAT, 
	amount_approved FLOAT, 
	status VARCHAR(20) NOT NULL, 
	notes VARCHAR(300), 
	submitted_at DATETIME, 
	created_by_id INTEGER, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	CONSTRAINT pk_insurance_claim PRIMARY KEY (id), 
	CONSTRAINT fk_insurance_claim_bill_id_bill FOREIGN KEY(bill_id) REFERENCES bill (id), 
	CONSTRAINT fk_insurance_claim_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_insurance_claim_bill_id ON insurance_claim (bill_id);

-- ---- lab_result
CREATE TABLE lab_result (
	id INTEGER NOT NULL, 
	lab_report_id INTEGER NOT NULL, 
	analyte VARCHAR(120) NOT NULL, 
	value_num FLOAT, 
	value_text VARCHAR(200), 
	unit VARCHAR(30), 
	ref_low FLOAT, 
	ref_high FLOAT, 
	ref_text VARCHAR(100), 
	critical_low FLOAT, 
	critical_high FLOAT, 
	flag VARCHAR(20) NOT NULL, 
	is_critical BOOLEAN NOT NULL, 
	status VARCHAR(12) NOT NULL, 
	version INTEGER NOT NULL, 
	supersedes_id INTEGER, 
	correction_reason VARCHAR(300), 
	entered_by_id INTEGER, 
	entered_at DATETIME NOT NULL, 
	CONSTRAINT pk_lab_result PRIMARY KEY (id), 
	CONSTRAINT fk_lab_result_lab_report_id_lab_report FOREIGN KEY(lab_report_id) REFERENCES lab_report (id), 
	CONSTRAINT fk_lab_result_supersedes_id_lab_result FOREIGN KEY(supersedes_id) REFERENCES lab_result (id), 
	CONSTRAINT fk_lab_result_entered_by_id_app_user FOREIGN KEY(entered_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_lab_result_lab_report_id ON lab_result (lab_report_id);

-- ---- medical_document
CREATE TABLE medical_document (
	id INTEGER NOT NULL, 
	public_id VARCHAR(36) NOT NULL, 
	patient_id INTEGER NOT NULL, 
	encounter_id INTEGER, 
	admission_id INTEGER, 
	lab_report_id INTEGER, 
	radiology_id INTEGER, 
	doc_type VARCHAR(40) NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	original_filename VARCHAR(200), 
	mime_type VARCHAR(80) NOT NULL, 
	size_bytes INTEGER NOT NULL, 
	sha256 VARCHAR(64) NOT NULL, 
	storage_backend VARCHAR(12) NOT NULL, 
	storage_key VARCHAR(200) NOT NULL, 
	uploaded_by_id INTEGER NOT NULL, 
	uploaded_at DATETIME NOT NULL, 
	processing_status VARCHAR(16) NOT NULL, 
	extraction_status VARCHAR(24) NOT NULL, 
	extraction_method VARCHAR(24), 
	extraction_quality FLOAT, 
	extraction_note VARCHAR(300), 
	page_count INTEGER, 
	review_status VARCHAR(20) NOT NULL, 
	reviewed_by_id INTEGER, 
	reviewed_at DATETIME, 
	version INTEGER NOT NULL, 
	supersedes_id INTEGER, 
	is_image BOOLEAN, 
	reprocess_count INTEGER, 
	patient_visible BOOLEAN DEFAULT 0 NOT NULL, 
	CONSTRAINT pk_medical_document PRIMARY KEY (id), 
	CONSTRAINT uq_medical_document_public_id UNIQUE (public_id), 
	CONSTRAINT fk_medical_document_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_medical_document_encounter_id_encounter FOREIGN KEY(encounter_id) REFERENCES encounter (id), 
	CONSTRAINT fk_medical_document_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_medical_document_lab_report_id_lab_report FOREIGN KEY(lab_report_id) REFERENCES lab_report (id), 
	CONSTRAINT fk_medical_document_radiology_id_radiology_record FOREIGN KEY(radiology_id) REFERENCES radiology_record (id), 
	CONSTRAINT fk_medical_document_uploaded_by_id_app_user FOREIGN KEY(uploaded_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_medical_document_reviewed_by_id_app_user FOREIGN KEY(reviewed_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_medical_document_supersedes_id_medical_document FOREIGN KEY(supersedes_id) REFERENCES medical_document (id)
);

CREATE INDEX ix_medical_document_patient_id ON medical_document (patient_id);

-- ---- medication_administration
CREATE TABLE medication_administration (
	id INTEGER NOT NULL, 
	prescription_id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	admission_id INTEGER, 
	scheduled_at DATETIME, 
	administered_at DATETIME, 
	status VARCHAR(12) NOT NULL, 
	dose_given VARCHAR(60), 
	identity_verified BOOLEAN, 
	allergies_checked BOOLEAN, 
	administered_by_id INTEGER, 
	note VARCHAR(300), 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_medication_administration PRIMARY KEY (id), 
	CONSTRAINT fk_medication_administration_prescription_id_prescription FOREIGN KEY(prescription_id) REFERENCES prescription (id), 
	CONSTRAINT fk_medication_administration_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_medication_administration_admission_id_admission FOREIGN KEY(admission_id) REFERENCES admission (id), 
	CONSTRAINT fk_medication_administration_administered_by_id_app_user FOREIGN KEY(administered_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_medication_administration_patient_id ON medication_administration (patient_id);
CREATE INDEX ix_medication_administration_prescription_id ON medication_administration (prescription_id);

-- ---- payment
CREATE TABLE payment (
	id INTEGER NOT NULL, 
	bill_id INTEGER NOT NULL, 
	kind VARCHAR(10) NOT NULL, 
	amount FLOAT NOT NULL, 
	method VARCHAR(30), 
	reference VARCHAR(80), 
	reason VARCHAR(300), 
	received_by_id INTEGER, 
	approved_by_id INTEGER, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_payment PRIMARY KEY (id), 
	CONSTRAINT ck_payment_amount_positive CHECK (amount > 0), 
	CONSTRAINT ck_payment_kind_valid CHECK (kind IN ('Payment','Refund')), 
	CONSTRAINT fk_payment_bill_id_bill FOREIGN KEY(bill_id) REFERENCES bill (id), 
	CONSTRAINT fk_payment_received_by_id_app_user FOREIGN KEY(received_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_payment_approved_by_id_app_user FOREIGN KEY(approved_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_payment_bill_id ON payment (bill_id);

-- ---- radiology_report_version
CREATE TABLE radiology_report_version (
	id INTEGER NOT NULL, 
	radiology_id INTEGER NOT NULL, 
	version INTEGER NOT NULL, 
	findings TEXT, 
	impression TEXT, 
	recommendations TEXT, 
	status VARCHAR(12), 
	change_reason VARCHAR(300), 
	author_id INTEGER, 
	created_at DATETIME NOT NULL, 
	CONSTRAINT pk_radiology_report_version PRIMARY KEY (id), 
	CONSTRAINT fk_radiology_report_version_radiology_id_radiology_record FOREIGN KEY(radiology_id) REFERENCES radiology_record (id), 
	CONSTRAINT fk_radiology_report_version_author_id_app_user FOREIGN KEY(author_id) REFERENCES app_user (id)
);

CREATE INDEX ix_radiology_report_version_radiology_id ON radiology_report_version (radiology_id);

-- ---- document_page
CREATE TABLE document_page (
	id INTEGER NOT NULL, 
	document_id INTEGER NOT NULL, 
	page_no INTEGER NOT NULL, 
	text TEXT, 
	method VARCHAR(16), 
	confidence FLOAT, 
	char_count INTEGER, 
	corrected_text TEXT, 
	corrected_by_id INTEGER, 
	CONSTRAINT pk_document_page PRIMARY KEY (id), 
	CONSTRAINT uq_document_page UNIQUE (document_id, page_no), 
	CONSTRAINT fk_document_page_document_id_medical_document FOREIGN KEY(document_id) REFERENCES medical_document (id), 
	CONSTRAINT fk_document_page_corrected_by_id_app_user FOREIGN KEY(corrected_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_document_page_document_id ON document_page (document_id);

-- ---- patient_deliverable
CREATE TABLE patient_deliverable (
	id INTEGER NOT NULL, 
	patient_id INTEGER NOT NULL, 
	kind VARCHAR(40) NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	ref_type VARCHAR(20), 
	ref_id INTEGER, 
	document_id INTEGER, 
	digital_available BOOLEAN NOT NULL, 
	physical_status VARCHAR(24) NOT NULL, 
	physical_note VARCHAR(300), 
	received_by_name VARCHAR(120), 
	handed_over_at DATETIME, 
	handed_over_by_id INTEGER, 
	created_by_id INTEGER, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	CONSTRAINT pk_patient_deliverable PRIMARY KEY (id), 
	CONSTRAINT ck_patient_deliverable_physical_status_valid CHECK (physical_status IN ('Not requested','Requested','Ready for collection','Handed over')), 
	CONSTRAINT uq_deliverable_ref UNIQUE (patient_id, ref_type, ref_id, kind), 
	CONSTRAINT fk_patient_deliverable_patient_id_patient FOREIGN KEY(patient_id) REFERENCES patient (id), 
	CONSTRAINT fk_patient_deliverable_document_id_medical_document FOREIGN KEY(document_id) REFERENCES medical_document (id), 
	CONSTRAINT fk_patient_deliverable_handed_over_by_id_app_user FOREIGN KEY(handed_over_by_id) REFERENCES app_user (id), 
	CONSTRAINT fk_patient_deliverable_created_by_id_app_user FOREIGN KEY(created_by_id) REFERENCES app_user (id)
);

CREATE INDEX ix_patient_deliverable_patient_id ON patient_deliverable (patient_id);
