--
-- PostgreSQL database dump
--

\restrict aEZcheN1lk1hCE6CdkUbzTQdealG9msK7jBvEWf1fJaSLs8tlSUcRybqbzn2lbv

-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.admission (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    ward character varying(80) NOT NULL,
    bed character varying(30),
    admitted_on character varying(10) NOT NULL,
    discharged_on character varying(10),
    status character varying(30),
    notes text,
    encounter_id integer,
    responsible_doctor_id integer,
    admitted_at timestamp with time zone,
    discharged_at timestamp with time zone,
    expected_discharge_on character varying(10),
    reason text,
    discharge_status character varying(20),
    discharge_plan text,
    discharge_summary text,
    discharge_authorized_by_id integer,
    discharge_authorized_at timestamp with time zone,
    created_by_id integer
);


--
-- Name: admission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.admission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: admission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.admission_id_seq OWNED BY public.admission.id;


--
-- Name: ai_conversation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ai_conversation (
    id character varying(36) NOT NULL,
    user_id integer NOT NULL,
    patient_id integer NOT NULL,
    title character varying(200),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone
);


--
-- Name: ai_message; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ai_message (
    id integer NOT NULL,
    conversation_id character varying(36) NOT NULL,
    role character varying(10) NOT NULL,
    content text NOT NULL,
    mode character varying(12),
    status character varying(24),
    sources json,
    limitations json,
    provider character varying(30),
    model character varying(60),
    created_at timestamp with time zone NOT NULL
);


--
-- Name: ai_message_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ai_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ai_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ai_message_id_seq OWNED BY public.ai_message.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: alert; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alert (
    id integer NOT NULL,
    rule_id integer NOT NULL,
    rule_version integer NOT NULL,
    rule_snapshot json,
    patient_id integer NOT NULL,
    admission_id integer,
    observation_id integer,
    severity character varying(10) NOT NULL,
    status character varying(12) NOT NULL,
    message character varying(300),
    triggered_at timestamp with time zone NOT NULL,
    last_triggered_at timestamp with time zone,
    occurrences integer NOT NULL,
    from_simulated_data boolean NOT NULL,
    responder_user_id integer,
    responder_role character varying(30),
    ack_by_id integer,
    ack_at timestamp with time zone,
    escalated_at timestamp with time zone,
    escalated_to_role character varying(30),
    resolved_by_id integer,
    resolved_at timestamp with time zone,
    resolution_note character varying(300),
    CONSTRAINT ck_alert_status_valid CHECK (((status)::text = ANY ((ARRAY['Open'::character varying, 'Acknowledged'::character varying, 'Escalated'::character varying, 'Resolved'::character varying])::text[])))
);


--
-- Name: alert_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.alert_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: alert_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.alert_id_seq OWNED BY public.alert.id;


--
-- Name: alert_rule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alert_rule (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    description character varying(300),
    rule_kind character varying(12) NOT NULL,
    type_code character varying(30),
    operator character varying(3),
    threshold double precision,
    severity character varying(10) NOT NULL,
    window_minutes integer,
    cooldown_minutes integer,
    active boolean NOT NULL,
    version integer NOT NULL,
    review_status character varying(12) NOT NULL,
    reviewed_by character varying(120),
    reviewed_at timestamp with time zone,
    created_by_id integer,
    updated_at timestamp with time zone,
    CONSTRAINT ck_alert_rule_kind_valid CHECK (((rule_kind)::text = ANY ((ARRAY['threshold'::character varying, 'missing'::character varying])::text[]))),
    CONSTRAINT ck_alert_rule_severity_valid CHECK (((severity)::text = ANY ((ARRAY['Info'::character varying, 'Warning'::character varying, 'Critical'::character varying])::text[])))
);


--
-- Name: alert_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.alert_rule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: alert_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.alert_rule_id_seq OWNED BY public.alert_rule.id;


--
-- Name: allergy; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.allergy (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    substance character varying(120) NOT NULL,
    reaction character varying(200),
    severity character varying(20),
    status character varying(20) NOT NULL,
    recorded_by_id integer,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: allergy_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.allergy_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: allergy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.allergy_id_seq OWNED BY public.allergy.id;


--
-- Name: app_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.app_user (
    id integer NOT NULL,
    email character varying(200) NOT NULL,
    name character varying(120) NOT NULL,
    password_hash character varying(300) NOT NULL,
    role character varying(30) NOT NULL,
    doctor_id integer,
    ward_id integer,
    is_active boolean NOT NULL,
    is_demo boolean NOT NULL,
    must_change_password boolean NOT NULL,
    failed_logins integer NOT NULL,
    locked_until timestamp with time zone,
    last_login_at timestamp with time zone,
    password_changed_at timestamp with time zone,
    session_epoch integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    created_by_id integer,
    patient_id integer,
    CONSTRAINT ck_app_user_patient_link_matches_role CHECK ((((role)::text = 'patient'::text) = (patient_id IS NOT NULL))),
    CONSTRAINT ck_app_user_role_valid CHECK (((role)::text = ANY ((ARRAY['super_admin'::character varying, 'hospital_admin'::character varying, 'doctor'::character varying, 'nurse'::character varying, 'lab_staff'::character varying, 'pharmacist'::character varying, 'radiology_staff'::character varying, 'billing_staff'::character varying, 'patient'::character varying])::text[])))
);


--
-- Name: app_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.app_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: app_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.app_user_id_seq OWNED BY public.app_user.id;


--
-- Name: appointment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.appointment (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_id integer NOT NULL,
    appointment_date character varying(10) NOT NULL,
    appointment_time character varying(5) NOT NULL,
    reason character varying(300),
    status character varying(30),
    duration_min integer,
    visit_type character varying(30),
    cancel_reason character varying(200),
    reschedule_count integer,
    created_by_id integer,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: appointment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.appointment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: appointment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.appointment_id_seq OWNED BY public.appointment.id;


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    action character varying(120) NOT NULL,
    details text,
    created_at timestamp with time zone NOT NULL,
    user_id integer,
    user_role character varying(30),
    category character varying(16),
    entity_type character varying(40),
    entity_id integer,
    patient_id integer,
    outcome character varying(10),
    ip character varying(64),
    request_id character varying(36)
);


--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: bed; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bed (
    id integer NOT NULL,
    room_id integer NOT NULL,
    ward_id integer NOT NULL,
    label character varying(30) NOT NULL,
    code character varying(40) NOT NULL,
    status character varying(20) NOT NULL,
    status_note character varying(200),
    status_changed_at timestamp with time zone,
    is_active boolean NOT NULL,
    CONSTRAINT ck_bed_status_valid CHECK (((status)::text = ANY ((ARRAY['Available'::character varying, 'Occupied'::character varying, 'Cleaning'::character varying, 'Reserved'::character varying, 'Maintenance'::character varying])::text[])))
);


--
-- Name: bed_assignment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bed_assignment (
    id integer NOT NULL,
    admission_id integer NOT NULL,
    bed_id integer NOT NULL,
    started_at timestamp with time zone NOT NULL,
    ended_at timestamp with time zone,
    reason character varying(30),
    end_reason character varying(30),
    moved_by_id integer,
    note character varying(300)
);


--
-- Name: bed_assignment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bed_assignment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bed_assignment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bed_assignment_id_seq OWNED BY public.bed_assignment.id;


--
-- Name: bed_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bed_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bed_id_seq OWNED BY public.bed.id;


--
-- Name: bill; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bill (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    description character varying(200) NOT NULL,
    consultation double precision,
    laboratory double precision,
    pharmacy double precision,
    room double precision,
    insurance_provider character varying(120),
    insurance_status character varying(40),
    paid boolean,
    created_at timestamp with time zone NOT NULL,
    other_charges double precision,
    encounter_id integer,
    admission_id integer,
    status character varying(12),
    created_by_id integer,
    voided_at timestamp with time zone
);


--
-- Name: bill_adjustment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bill_adjustment (
    id integer NOT NULL,
    bill_id integer NOT NULL,
    kind character varying(20) NOT NULL,
    amount double precision NOT NULL,
    reason character varying(300) NOT NULL,
    requested_by_id integer,
    approved_by_id integer,
    created_at timestamp with time zone NOT NULL,
    CONSTRAINT ck_bill_adjustment_amount_positive CHECK ((amount > (0)::double precision))
);


--
-- Name: bill_adjustment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bill_adjustment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bill_adjustment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bill_adjustment_id_seq OWNED BY public.bill_adjustment.id;


--
-- Name: bill_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bill_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bill_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bill_id_seq OWNED BY public.bill.id;


--
-- Name: care_plan; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.care_plan (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    admission_id integer,
    title character varying(200) NOT NULL,
    goals text,
    status character varying(20) NOT NULL,
    author_id integer,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: care_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.care_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: care_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.care_plan_id_seq OWNED BY public.care_plan.id;


--
-- Name: care_task; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.care_task (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    admission_id integer,
    care_plan_id integer,
    title character varying(200) NOT NULL,
    category character varying(30) NOT NULL,
    assigned_role character varying(30),
    assigned_user_id integer,
    due_at timestamp with time zone,
    status character varying(20) NOT NULL,
    priority character varying(20) NOT NULL,
    notes text,
    completed_at timestamp with time zone,
    completed_by_id integer,
    created_by_id integer,
    created_at timestamp with time zone NOT NULL,
    CONSTRAINT ck_care_task_status_valid CHECK (((status)::text = ANY ((ARRAY['Pending'::character varying, 'Done'::character varying, 'Cancelled'::character varying])::text[])))
);


--
-- Name: care_task_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.care_task_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: care_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.care_task_id_seq OWNED BY public.care_task.id;


--
-- Name: clinical_note; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clinical_note (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    encounter_id integer,
    admission_id integer,
    author_id integer NOT NULL,
    note_type character varying(30) NOT NULL,
    body text NOT NULL,
    status character varying(20) NOT NULL,
    amends_note_id integer,
    amendment_reason character varying(300),
    created_at timestamp with time zone NOT NULL,
    CONSTRAINT ck_clinical_note_status_valid CHECK (((status)::text = ANY ((ARRAY['Final'::character varying, 'Superseded'::character varying])::text[])))
);


--
-- Name: clinical_note_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.clinical_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: clinical_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.clinical_note_id_seq OWNED BY public.clinical_note.id;


--
-- Name: critical_ack; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.critical_ack (
    id integer NOT NULL,
    source_type character varying(12) NOT NULL,
    source_id integer NOT NULL,
    patient_id integer NOT NULL,
    summary character varying(300),
    notify_user_id integer,
    status character varying(12) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    ack_by_id integer,
    ack_at timestamp with time zone,
    ack_note character varying(300),
    escalated_at timestamp with time zone,
    escalated_to_role character varying(30),
    CONSTRAINT ck_critical_ack_status_valid CHECK (((status)::text = ANY ((ARRAY['Pending'::character varying, 'Acknowledged'::character varying, 'Escalated'::character varying])::text[])))
);


--
-- Name: critical_ack_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.critical_ack_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: critical_ack_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.critical_ack_id_seq OWNED BY public.critical_ack.id;


--
-- Name: department; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.department (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: department_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.department_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: department_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.department_id_seq OWNED BY public.department.id;


--
-- Name: dispense_event; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dispense_event (
    id integer NOT NULL,
    prescription_id integer NOT NULL,
    medicine_id integer NOT NULL,
    quantity integer NOT NULL,
    dispensed_by_id integer NOT NULL,
    dispensed_at timestamp with time zone NOT NULL,
    warnings_acknowledged json,
    note character varying(300),
    CONSTRAINT ck_dispense_event_qty_positive CHECK ((quantity > 0))
);


--
-- Name: dispense_event_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dispense_event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dispense_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dispense_event_id_seq OWNED BY public.dispense_event.id;


--
-- Name: doctor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.doctor (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    specialty character varying(100) NOT NULL,
    department character varying(100),
    phone character varying(30),
    available boolean,
    registration_no character varying(60)
);


--
-- Name: doctor_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.doctor_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: doctor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.doctor_id_seq OWNED BY public.doctor.id;


--
-- Name: document_page; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.document_page (
    id integer NOT NULL,
    document_id integer NOT NULL,
    page_no integer NOT NULL,
    text text,
    method character varying(16),
    confidence double precision,
    char_count integer,
    corrected_text text,
    corrected_by_id integer
);


--
-- Name: document_page_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.document_page_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: document_page_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.document_page_id_seq OWNED BY public.document_page.id;


--
-- Name: encounter; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.encounter (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    encounter_type character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    doctor_id integer,
    appointment_id integer,
    chief_complaint character varying(300),
    started_at timestamp with time zone,
    ended_at timestamp with time zone,
    created_by_id integer
);


--
-- Name: encounter_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.encounter_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: encounter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.encounter_id_seq OWNED BY public.encounter.id;


--
-- Name: follow_up; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.follow_up (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    encounter_id integer,
    admission_id integer,
    due_on character varying(10),
    instructions text,
    appointment_id integer,
    status character varying(20) NOT NULL,
    created_by_id integer,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: follow_up_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.follow_up_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: follow_up_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.follow_up_id_seq OWNED BY public.follow_up.id;


--
-- Name: handover; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.handover (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    admission_id integer,
    ward_id integer,
    kind character varying(20) NOT NULL,
    shift character varying(20),
    situation text,
    background text,
    assessment text,
    recommendation text,
    is_auto_draft boolean NOT NULL,
    author_id integer,
    reviewed_by_id integer,
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: handover_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.handover_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: handover_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.handover_id_seq OWNED BY public.handover.id;


--
-- Name: insurance_claim; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.insurance_claim (
    id integer NOT NULL,
    bill_id integer NOT NULL,
    provider character varying(120) NOT NULL,
    policy_no character varying(60),
    claim_no character varying(60),
    amount_claimed double precision,
    amount_approved double precision,
    status character varying(20) NOT NULL,
    notes character varying(300),
    submitted_at timestamp with time zone,
    created_by_id integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


--
-- Name: insurance_claim_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.insurance_claim_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: insurance_claim_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.insurance_claim_id_seq OWNED BY public.insurance_claim.id;


--
-- Name: intake_output; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.intake_output (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    admission_id integer,
    kind character varying(10) NOT NULL,
    item character varying(100),
    amount_ml double precision NOT NULL,
    recorded_by_id integer,
    recorded_at timestamp with time zone NOT NULL,
    CONSTRAINT ck_intake_output_amount_nonneg CHECK ((amount_ml >= (0)::double precision)),
    CONSTRAINT ck_intake_output_kind_valid CHECK (((kind)::text = ANY ((ARRAY['Intake'::character varying, 'Output'::character varying])::text[])))
);


--
-- Name: intake_output_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.intake_output_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: intake_output_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.intake_output_id_seq OWNED BY public.intake_output.id;


--
-- Name: lab_report; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lab_report (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    test_name character varying(120) NOT NULL,
    sample_date character varying(10) NOT NULL,
    result text,
    status character varying(30),
    ordered_by character varying(120),
    encounter_id integer,
    admission_id integer,
    ordered_by_id integer,
    accession_no character varying(30),
    priority character varying(10),
    specimen_type character varying(60),
    clinical_info character varying(300),
    ordered_at timestamp with time zone,
    collected_at timestamp with time zone,
    collected_by_id integer,
    received_at timestamp with time zone,
    resulted_at timestamp with time zone,
    resulted_by_id integer,
    verified_at timestamp with time zone,
    verified_by_id integer,
    released_at timestamp with time zone,
    released_by_id integer,
    rejected_at timestamp with time zone,
    rejected_reason character varying(300),
    amendment_count integer
);


--
-- Name: lab_report_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.lab_report_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: lab_report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.lab_report_id_seq OWNED BY public.lab_report.id;


--
-- Name: lab_result; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lab_result (
    id integer NOT NULL,
    lab_report_id integer NOT NULL,
    analyte character varying(120) NOT NULL,
    value_num double precision,
    value_text character varying(200),
    unit character varying(30),
    ref_low double precision,
    ref_high double precision,
    ref_text character varying(100),
    critical_low double precision,
    critical_high double precision,
    flag character varying(20) NOT NULL,
    is_critical boolean NOT NULL,
    status character varying(12) NOT NULL,
    version integer NOT NULL,
    supersedes_id integer,
    correction_reason character varying(300),
    entered_by_id integer,
    entered_at timestamp with time zone NOT NULL
);


--
-- Name: lab_result_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.lab_result_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: lab_result_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.lab_result_id_seq OWNED BY public.lab_result.id;


--
-- Name: med_reconciliation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.med_reconciliation (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    admission_id integer,
    pharmacist_id integer,
    items json,
    notes text,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: med_reconciliation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.med_reconciliation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: med_reconciliation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.med_reconciliation_id_seq OWNED BY public.med_reconciliation.id;


--
-- Name: medical_document; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.medical_document (
    id integer NOT NULL,
    public_id character varying(36) NOT NULL,
    patient_id integer NOT NULL,
    encounter_id integer,
    admission_id integer,
    lab_report_id integer,
    radiology_id integer,
    doc_type character varying(40) NOT NULL,
    title character varying(200) NOT NULL,
    original_filename character varying(200),
    mime_type character varying(80) NOT NULL,
    size_bytes integer NOT NULL,
    sha256 character varying(64) NOT NULL,
    storage_backend character varying(12) NOT NULL,
    storage_key character varying(200) NOT NULL,
    uploaded_by_id integer NOT NULL,
    uploaded_at timestamp with time zone NOT NULL,
    processing_status character varying(16) NOT NULL,
    extraction_status character varying(24) NOT NULL,
    extraction_method character varying(24),
    extraction_quality double precision,
    extraction_note character varying(300),
    page_count integer,
    review_status character varying(20) NOT NULL,
    reviewed_by_id integer,
    reviewed_at timestamp with time zone,
    version integer NOT NULL,
    supersedes_id integer,
    is_image boolean,
    reprocess_count integer,
    patient_visible boolean DEFAULT false NOT NULL
);


--
-- Name: medical_document_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.medical_document_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: medical_document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.medical_document_id_seq OWNED BY public.medical_document.id;


--
-- Name: medication_administration; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.medication_administration (
    id integer NOT NULL,
    prescription_id integer NOT NULL,
    patient_id integer NOT NULL,
    admission_id integer,
    scheduled_at timestamp with time zone,
    administered_at timestamp with time zone,
    status character varying(12) NOT NULL,
    dose_given character varying(60),
    identity_verified boolean,
    allergies_checked boolean,
    administered_by_id integer,
    note character varying(300),
    created_at timestamp with time zone NOT NULL
);


--
-- Name: medication_administration_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.medication_administration_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: medication_administration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.medication_administration_id_seq OWNED BY public.medication_administration.id;


--
-- Name: medicine; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.medicine (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    category character varying(80),
    stock integer,
    reorder_level integer,
    unit_price double precision,
    expiry_date character varying(10),
    generic_name character varying(120),
    strength character varying(40),
    form character varying(40),
    batch_no character varying(40),
    is_active boolean,
    CONSTRAINT ck_medicine_stock_nonneg CHECK ((stock >= 0))
);


--
-- Name: medicine_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.medicine_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: medicine_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.medicine_id_seq OWNED BY public.medicine.id;


--
-- Name: monitoring_device; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.monitoring_device (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    kind character varying(60),
    patient_id integer,
    is_simulated boolean NOT NULL,
    is_active boolean NOT NULL,
    api_key_hash character varying(128),
    api_key_prefix character varying(12),
    last_seen_at timestamp with time zone,
    created_by_id integer,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: monitoring_device_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.monitoring_device_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: monitoring_device_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.monitoring_device_id_seq OWNED BY public.monitoring_device.id;


--
-- Name: notification; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notification (
    id integer NOT NULL,
    user_id integer,
    role character varying(30),
    kind character varying(40) NOT NULL,
    severity character varying(10),
    title character varying(200) NOT NULL,
    body character varying(400),
    patient_id integer,
    ref_type character varying(30),
    ref_id integer,
    delivery character varying(12),
    created_at timestamp with time zone NOT NULL,
    read_at timestamp with time zone
);


--
-- Name: notification_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notification_id_seq OWNED BY public.notification.id;


--
-- Name: observation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.observation (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    admission_id integer,
    encounter_id integer,
    type_code character varying(30) NOT NULL,
    value_num double precision NOT NULL,
    unit character varying(20) NOT NULL,
    observed_at timestamp with time zone NOT NULL,
    recorded_at timestamp with time zone NOT NULL,
    source character varying(12) NOT NULL,
    device_id integer,
    recorded_by_id integer,
    validation_status character varying(20) NOT NULL,
    supersedes_id integer,
    correction_reason character varying(300),
    group_id character varying(36),
    note character varying(300),
    CONSTRAINT ck_observation_source_valid CHECK (((source)::text = ANY ((ARRAY['manual'::character varying, 'device'::character varying, 'simulated'::character varying])::text[]))),
    CONSTRAINT ck_observation_validation_valid CHECK (((validation_status)::text = ANY ((ARRAY['Valid'::character varying, 'Unverified'::character varying, 'Corrected'::character varying, 'Entered in error'::character varying])::text[])))
);


--
-- Name: observation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.observation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: observation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.observation_id_seq OWNED BY public.observation.id;


--
-- Name: observation_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.observation_type (
    code character varying(30) NOT NULL,
    label character varying(80) NOT NULL,
    unit character varying(20) NOT NULL,
    plausible_min double precision,
    plausible_max double precision,
    decimals integer,
    is_active boolean NOT NULL
);


--
-- Name: patient; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.patient (
    id integer NOT NULL,
    patient_code character varying(20) NOT NULL,
    name character varying(120) NOT NULL,
    dob character varying(10),
    gender character varying(30),
    phone character varying(30),
    email character varying(120),
    blood_group character varying(5),
    allergies text,
    emergency_contact character varying(120),
    medical_history text,
    created_at timestamp with time zone NOT NULL,
    address text,
    emergency_contact_phone character varying(30),
    emergency_contact_relation character varying(60),
    identifier_label character varying(60),
    identifier_last4 character varying(4),
    identity_verified boolean,
    identity_verified_by_id integer,
    identity_verified_at timestamp with time zone,
    consent_data_sharing boolean,
    consent_notes text,
    insurance_provider character varying(120),
    insurance_policy_no character varying(60),
    data_origin character varying(20),
    archived_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: patient_assignment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.patient_assignment (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    user_id integer NOT NULL,
    relation character varying(20) NOT NULL,
    active boolean NOT NULL,
    starts_at timestamp with time zone,
    ends_at timestamp with time zone,
    created_by_id integer
);


--
-- Name: patient_assignment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.patient_assignment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: patient_assignment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.patient_assignment_id_seq OWNED BY public.patient_assignment.id;


--
-- Name: patient_deliverable; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.patient_deliverable (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    kind character varying(40) NOT NULL,
    title character varying(200) NOT NULL,
    ref_type character varying(20),
    ref_id integer,
    document_id integer,
    digital_available boolean NOT NULL,
    physical_status character varying(24) NOT NULL,
    physical_note character varying(300),
    received_by_name character varying(120),
    handed_over_at timestamp with time zone,
    handed_over_by_id integer,
    created_by_id integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone,
    CONSTRAINT ck_patient_deliverable_physical_status_valid CHECK (((physical_status)::text = ANY ((ARRAY['Not requested'::character varying, 'Requested'::character varying, 'Ready for collection'::character varying, 'Handed over'::character varying])::text[])))
);


--
-- Name: patient_deliverable_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.patient_deliverable_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: patient_deliverable_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.patient_deliverable_id_seq OWNED BY public.patient_deliverable.id;


--
-- Name: patient_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.patient_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: patient_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.patient_id_seq OWNED BY public.patient.id;


--
-- Name: payment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payment (
    id integer NOT NULL,
    bill_id integer NOT NULL,
    kind character varying(10) NOT NULL,
    amount double precision NOT NULL,
    method character varying(30),
    reference character varying(80),
    reason character varying(300),
    received_by_id integer,
    approved_by_id integer,
    created_at timestamp with time zone NOT NULL,
    CONSTRAINT ck_payment_amount_positive CHECK ((amount > (0)::double precision)),
    CONSTRAINT ck_payment_kind_valid CHECK (((kind)::text = ANY ((ARRAY['Payment'::character varying, 'Refund'::character varying])::text[])))
);


--
-- Name: payment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payment_id_seq OWNED BY public.payment.id;


--
-- Name: prescription; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prescription (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_name character varying(120),
    medicine character varying(120) NOT NULL,
    dosage character varying(120),
    instructions text,
    created_at timestamp with time zone NOT NULL,
    ordered_by_id integer,
    encounter_id integer,
    admission_id integer,
    medicine_id integer,
    route character varying(30),
    frequency character varying(60),
    duration_days integer,
    quantity integer,
    is_prn boolean,
    status character varying(24),
    allergy_override_reason character varying(300),
    warnings json,
    verified_by_id integer,
    verified_at timestamp with time zone,
    cancelled_reason character varying(300),
    dispensed_quantity integer
);


--
-- Name: prescription_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.prescription_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: prescription_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.prescription_id_seq OWNED BY public.prescription.id;


--
-- Name: problem; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.problem (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    encounter_id integer,
    description character varying(300) NOT NULL,
    code character varying(30),
    status character varying(20) NOT NULL,
    onset_on character varying(10),
    recorded_by_id integer,
    created_at timestamp with time zone NOT NULL,
    resolved_at timestamp with time zone
);


--
-- Name: problem_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.problem_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: problem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.problem_id_seq OWNED BY public.problem.id;


--
-- Name: radiology_record; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.radiology_record (
    id integer NOT NULL,
    patient_id integer NOT NULL,
    modality character varying(50) NOT NULL,
    study_date character varying(10) NOT NULL,
    findings text,
    report_status character varying(30),
    encounter_id integer,
    admission_id integer,
    ordered_by_id integer,
    order_status character varying(12),
    study_description character varying(200),
    indication character varying(300),
    priority character varying(10),
    scheduled_at timestamp with time zone,
    performed_at timestamp with time zone,
    performed_by_id integer,
    impression text,
    recommendations text,
    reported_by_id integer,
    reported_at timestamp with time zone,
    authorized_by_id integer,
    authorized_at timestamp with time zone,
    urgent_finding boolean,
    amendment_count integer,
    ordered_at timestamp with time zone
);


--
-- Name: radiology_record_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.radiology_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: radiology_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.radiology_record_id_seq OWNED BY public.radiology_record.id;


--
-- Name: radiology_report_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.radiology_report_version (
    id integer NOT NULL,
    radiology_id integer NOT NULL,
    version integer NOT NULL,
    findings text,
    impression text,
    recommendations text,
    status character varying(12),
    change_reason character varying(300),
    author_id integer,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: radiology_report_version_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.radiology_report_version_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: radiology_report_version_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.radiology_report_version_id_seq OWNED BY public.radiology_report_version.id;


--
-- Name: room; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.room (
    id integer NOT NULL,
    ward_id integer NOT NULL,
    label character varying(30) NOT NULL
);


--
-- Name: room_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.room_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: room_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.room_id_seq OWNED BY public.room.id;


--
-- Name: stock_movement; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stock_movement (
    id integer NOT NULL,
    medicine_id integer NOT NULL,
    delta integer NOT NULL,
    balance_after integer NOT NULL,
    reason character varying(30) NOT NULL,
    ref_type character varying(30),
    ref_id integer,
    user_id integer,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: stock_movement_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.stock_movement_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: stock_movement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.stock_movement_id_seq OWNED BY public.stock_movement.id;


--
-- Name: system_setting; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_setting (
    key character varying(80) NOT NULL,
    value json,
    updated_by_id integer,
    updated_at timestamp with time zone
);


--
-- Name: ward; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ward (
    id integer NOT NULL,
    name character varying(80) NOT NULL,
    department_id integer,
    specialty character varying(100),
    floor character varying(20),
    daily_rate double precision NOT NULL,
    is_active boolean NOT NULL
);


--
-- Name: ward_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ward_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ward_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ward_id_seq OWNED BY public.ward.id;


--
-- Name: admission id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admission ALTER COLUMN id SET DEFAULT nextval('public.admission_id_seq'::regclass);


--
-- Name: ai_message id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_message ALTER COLUMN id SET DEFAULT nextval('public.ai_message_id_seq'::regclass);


--
-- Name: alert id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert ALTER COLUMN id SET DEFAULT nextval('public.alert_id_seq'::regclass);


--
-- Name: alert_rule id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert_rule ALTER COLUMN id SET DEFAULT nextval('public.alert_rule_id_seq'::regclass);


--
-- Name: allergy id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allergy ALTER COLUMN id SET DEFAULT nextval('public.allergy_id_seq'::regclass);


--
-- Name: app_user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user ALTER COLUMN id SET DEFAULT nextval('public.app_user_id_seq'::regclass);


--
-- Name: appointment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointment ALTER COLUMN id SET DEFAULT nextval('public.appointment_id_seq'::regclass);


--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Name: bed id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed ALTER COLUMN id SET DEFAULT nextval('public.bed_id_seq'::regclass);


--
-- Name: bed_assignment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed_assignment ALTER COLUMN id SET DEFAULT nextval('public.bed_assignment_id_seq'::regclass);


--
-- Name: bill id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill ALTER COLUMN id SET DEFAULT nextval('public.bill_id_seq'::regclass);


--
-- Name: bill_adjustment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill_adjustment ALTER COLUMN id SET DEFAULT nextval('public.bill_adjustment_id_seq'::regclass);


--
-- Name: care_plan id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_plan ALTER COLUMN id SET DEFAULT nextval('public.care_plan_id_seq'::regclass);


--
-- Name: care_task id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_task ALTER COLUMN id SET DEFAULT nextval('public.care_task_id_seq'::regclass);


--
-- Name: clinical_note id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clinical_note ALTER COLUMN id SET DEFAULT nextval('public.clinical_note_id_seq'::regclass);


--
-- Name: critical_ack id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.critical_ack ALTER COLUMN id SET DEFAULT nextval('public.critical_ack_id_seq'::regclass);


--
-- Name: department id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.department ALTER COLUMN id SET DEFAULT nextval('public.department_id_seq'::regclass);


--
-- Name: dispense_event id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dispense_event ALTER COLUMN id SET DEFAULT nextval('public.dispense_event_id_seq'::regclass);


--
-- Name: doctor id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doctor ALTER COLUMN id SET DEFAULT nextval('public.doctor_id_seq'::regclass);


--
-- Name: document_page id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_page ALTER COLUMN id SET DEFAULT nextval('public.document_page_id_seq'::regclass);


--
-- Name: encounter id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounter ALTER COLUMN id SET DEFAULT nextval('public.encounter_id_seq'::regclass);


--
-- Name: follow_up id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follow_up ALTER COLUMN id SET DEFAULT nextval('public.follow_up_id_seq'::regclass);


--
-- Name: handover id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover ALTER COLUMN id SET DEFAULT nextval('public.handover_id_seq'::regclass);


--
-- Name: insurance_claim id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.insurance_claim ALTER COLUMN id SET DEFAULT nextval('public.insurance_claim_id_seq'::regclass);


--
-- Name: intake_output id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intake_output ALTER COLUMN id SET DEFAULT nextval('public.intake_output_id_seq'::regclass);


--
-- Name: lab_report id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report ALTER COLUMN id SET DEFAULT nextval('public.lab_report_id_seq'::regclass);


--
-- Name: lab_result id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_result ALTER COLUMN id SET DEFAULT nextval('public.lab_result_id_seq'::regclass);


--
-- Name: med_reconciliation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.med_reconciliation ALTER COLUMN id SET DEFAULT nextval('public.med_reconciliation_id_seq'::regclass);


--
-- Name: medical_document id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document ALTER COLUMN id SET DEFAULT nextval('public.medical_document_id_seq'::regclass);


--
-- Name: medication_administration id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medication_administration ALTER COLUMN id SET DEFAULT nextval('public.medication_administration_id_seq'::regclass);


--
-- Name: medicine id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medicine ALTER COLUMN id SET DEFAULT nextval('public.medicine_id_seq'::regclass);


--
-- Name: monitoring_device id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monitoring_device ALTER COLUMN id SET DEFAULT nextval('public.monitoring_device_id_seq'::regclass);


--
-- Name: notification id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification ALTER COLUMN id SET DEFAULT nextval('public.notification_id_seq'::regclass);


--
-- Name: observation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation ALTER COLUMN id SET DEFAULT nextval('public.observation_id_seq'::regclass);


--
-- Name: patient id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient ALTER COLUMN id SET DEFAULT nextval('public.patient_id_seq'::regclass);


--
-- Name: patient_assignment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_assignment ALTER COLUMN id SET DEFAULT nextval('public.patient_assignment_id_seq'::regclass);


--
-- Name: patient_deliverable id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_deliverable ALTER COLUMN id SET DEFAULT nextval('public.patient_deliverable_id_seq'::regclass);


--
-- Name: payment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment ALTER COLUMN id SET DEFAULT nextval('public.payment_id_seq'::regclass);


--
-- Name: prescription id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescription ALTER COLUMN id SET DEFAULT nextval('public.prescription_id_seq'::regclass);


--
-- Name: problem id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.problem ALTER COLUMN id SET DEFAULT nextval('public.problem_id_seq'::regclass);


--
-- Name: radiology_record id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_record ALTER COLUMN id SET DEFAULT nextval('public.radiology_record_id_seq'::regclass);


--
-- Name: radiology_report_version id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_report_version ALTER COLUMN id SET DEFAULT nextval('public.radiology_report_version_id_seq'::regclass);


--
-- Name: room id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.room ALTER COLUMN id SET DEFAULT nextval('public.room_id_seq'::regclass);


--
-- Name: stock_movement id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movement ALTER COLUMN id SET DEFAULT nextval('public.stock_movement_id_seq'::regclass);


--
-- Name: ward id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ward ALTER COLUMN id SET DEFAULT nextval('public.ward_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

\unrestrict aEZcheN1lk1hCE6CdkUbzTQdealG9msK7jBvEWf1fJaSLs8tlSUcRybqbzn2lbv

