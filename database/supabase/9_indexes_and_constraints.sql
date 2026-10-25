--
-- PostgreSQL database dump
--

\restrict b0tMjCJuhbVpX8afBDvSl2z3bI0DmP4KmBMFwZA3OiKuZZnHx7vHQTgKXneokFH

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

--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: admission pk_admission; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admission
    ADD CONSTRAINT pk_admission PRIMARY KEY (id);


--
-- Name: ai_conversation pk_ai_conversation; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_conversation
    ADD CONSTRAINT pk_ai_conversation PRIMARY KEY (id);


--
-- Name: ai_message pk_ai_message; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_message
    ADD CONSTRAINT pk_ai_message PRIMARY KEY (id);


--
-- Name: alert pk_alert; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert
    ADD CONSTRAINT pk_alert PRIMARY KEY (id);


--
-- Name: alert_rule pk_alert_rule; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert_rule
    ADD CONSTRAINT pk_alert_rule PRIMARY KEY (id);


--
-- Name: allergy pk_allergy; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allergy
    ADD CONSTRAINT pk_allergy PRIMARY KEY (id);


--
-- Name: app_user pk_app_user; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT pk_app_user PRIMARY KEY (id);


--
-- Name: appointment pk_appointment; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointment
    ADD CONSTRAINT pk_appointment PRIMARY KEY (id);


--
-- Name: audit_log pk_audit_log; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT pk_audit_log PRIMARY KEY (id);


--
-- Name: bed pk_bed; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed
    ADD CONSTRAINT pk_bed PRIMARY KEY (id);


--
-- Name: bed_assignment pk_bed_assignment; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed_assignment
    ADD CONSTRAINT pk_bed_assignment PRIMARY KEY (id);


--
-- Name: bill pk_bill; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill
    ADD CONSTRAINT pk_bill PRIMARY KEY (id);


--
-- Name: bill_adjustment pk_bill_adjustment; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill_adjustment
    ADD CONSTRAINT pk_bill_adjustment PRIMARY KEY (id);


--
-- Name: care_plan pk_care_plan; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_plan
    ADD CONSTRAINT pk_care_plan PRIMARY KEY (id);


--
-- Name: care_task pk_care_task; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_task
    ADD CONSTRAINT pk_care_task PRIMARY KEY (id);


--
-- Name: clinical_note pk_clinical_note; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clinical_note
    ADD CONSTRAINT pk_clinical_note PRIMARY KEY (id);


--
-- Name: critical_ack pk_critical_ack; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.critical_ack
    ADD CONSTRAINT pk_critical_ack PRIMARY KEY (id);


--
-- Name: department pk_department; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT pk_department PRIMARY KEY (id);


--
-- Name: dispense_event pk_dispense_event; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dispense_event
    ADD CONSTRAINT pk_dispense_event PRIMARY KEY (id);


--
-- Name: doctor pk_doctor; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doctor
    ADD CONSTRAINT pk_doctor PRIMARY KEY (id);


--
-- Name: document_page pk_document_page; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_page
    ADD CONSTRAINT pk_document_page PRIMARY KEY (id);


--
-- Name: encounter pk_encounter; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounter
    ADD CONSTRAINT pk_encounter PRIMARY KEY (id);


--
-- Name: follow_up pk_follow_up; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follow_up
    ADD CONSTRAINT pk_follow_up PRIMARY KEY (id);


--
-- Name: handover pk_handover; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover
    ADD CONSTRAINT pk_handover PRIMARY KEY (id);


--
-- Name: insurance_claim pk_insurance_claim; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.insurance_claim
    ADD CONSTRAINT pk_insurance_claim PRIMARY KEY (id);


--
-- Name: intake_output pk_intake_output; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intake_output
    ADD CONSTRAINT pk_intake_output PRIMARY KEY (id);


--
-- Name: lab_report pk_lab_report; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT pk_lab_report PRIMARY KEY (id);


--
-- Name: lab_result pk_lab_result; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_result
    ADD CONSTRAINT pk_lab_result PRIMARY KEY (id);


--
-- Name: med_reconciliation pk_med_reconciliation; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.med_reconciliation
    ADD CONSTRAINT pk_med_reconciliation PRIMARY KEY (id);


--
-- Name: medical_document pk_medical_document; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document
    ADD CONSTRAINT pk_medical_document PRIMARY KEY (id);


--
-- Name: medication_administration pk_medication_administration; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medication_administration
    ADD CONSTRAINT pk_medication_administration PRIMARY KEY (id);


--
-- Name: medicine pk_medicine; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medicine
    ADD CONSTRAINT pk_medicine PRIMARY KEY (id);


--
-- Name: monitoring_device pk_monitoring_device; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monitoring_device
    ADD CONSTRAINT pk_monitoring_device PRIMARY KEY (id);


--
-- Name: notification pk_notification; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT pk_notification PRIMARY KEY (id);


--
-- Name: observation pk_observation; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT pk_observation PRIMARY KEY (id);


--
-- Name: observation_type pk_observation_type; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation_type
    ADD CONSTRAINT pk_observation_type PRIMARY KEY (code);


--
-- Name: patient pk_patient; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient
    ADD CONSTRAINT pk_patient PRIMARY KEY (id);


--
-- Name: patient_assignment pk_patient_assignment; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_assignment
    ADD CONSTRAINT pk_patient_assignment PRIMARY KEY (id);


--
-- Name: patient_deliverable pk_patient_deliverable; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_deliverable
    ADD CONSTRAINT pk_patient_deliverable PRIMARY KEY (id);


--
-- Name: payment pk_payment; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT pk_payment PRIMARY KEY (id);


--
-- Name: prescription pk_prescription; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT pk_prescription PRIMARY KEY (id);


--
-- Name: problem pk_problem; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.problem
    ADD CONSTRAINT pk_problem PRIMARY KEY (id);


--
-- Name: radiology_record pk_radiology_record; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_record
    ADD CONSTRAINT pk_radiology_record PRIMARY KEY (id);


--
-- Name: radiology_report_version pk_radiology_report_version; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_report_version
    ADD CONSTRAINT pk_radiology_report_version PRIMARY KEY (id);


--
-- Name: room pk_room; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.room
    ADD CONSTRAINT pk_room PRIMARY KEY (id);


--
-- Name: stock_movement pk_stock_movement; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movement
    ADD CONSTRAINT pk_stock_movement PRIMARY KEY (id);


--
-- Name: system_setting pk_system_setting; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_setting
    ADD CONSTRAINT pk_system_setting PRIMARY KEY (key);


--
-- Name: ward pk_ward; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ward
    ADD CONSTRAINT pk_ward PRIMARY KEY (id);


--
-- Name: app_user uq_app_user_doctor_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT uq_app_user_doctor_id UNIQUE (doctor_id);


--
-- Name: app_user uq_app_user_email; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT uq_app_user_email UNIQUE (email);


--
-- Name: app_user uq_app_user_patient_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT uq_app_user_patient_id UNIQUE (patient_id);


--
-- Name: bed uq_bed_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed
    ADD CONSTRAINT uq_bed_code UNIQUE (code);


--
-- Name: bed uq_bed_room_label; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed
    ADD CONSTRAINT uq_bed_room_label UNIQUE (room_id, label);


--
-- Name: critical_ack uq_critical_ack_source; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.critical_ack
    ADD CONSTRAINT uq_critical_ack_source UNIQUE (source_type, source_id);


--
-- Name: patient_deliverable uq_deliverable_ref; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_deliverable
    ADD CONSTRAINT uq_deliverable_ref UNIQUE (patient_id, ref_type, ref_id, kind);


--
-- Name: department uq_department_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT uq_department_name UNIQUE (name);


--
-- Name: document_page uq_document_page; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_page
    ADD CONSTRAINT uq_document_page UNIQUE (document_id, page_no);


--
-- Name: lab_report uq_lab_report_accession_no; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT uq_lab_report_accession_no UNIQUE (accession_no);


--
-- Name: medical_document uq_medical_document_public_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document
    ADD CONSTRAINT uq_medical_document_public_id UNIQUE (public_id);


--
-- Name: medicine uq_medicine_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medicine
    ADD CONSTRAINT uq_medicine_name UNIQUE (name);


--
-- Name: patient uq_patient_patient_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient
    ADD CONSTRAINT uq_patient_patient_code UNIQUE (patient_code);


--
-- Name: room uq_room_ward_label; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.room
    ADD CONSTRAINT uq_room_ward_label UNIQUE (ward_id, label);


--
-- Name: ward uq_ward_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ward
    ADD CONSTRAINT uq_ward_name UNIQUE (name);


--
-- Name: ix_ai_conversation_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_conversation_patient_id ON public.ai_conversation USING btree (patient_id);


--
-- Name: ix_ai_conversation_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_conversation_user_id ON public.ai_conversation USING btree (user_id);


--
-- Name: ix_ai_message_conversation_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ai_message_conversation_id ON public.ai_message USING btree (conversation_id);


--
-- Name: ix_alert_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_alert_patient_id ON public.alert USING btree (patient_id);


--
-- Name: ix_allergy_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_allergy_patient_id ON public.allergy USING btree (patient_id);


--
-- Name: ix_app_user_role; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_app_user_role ON public.app_user USING btree (role);


--
-- Name: ix_appointment_doctor_day; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_appointment_doctor_day ON public.appointment USING btree (doctor_id, appointment_date);


--
-- Name: ix_appointment_patient; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_appointment_patient ON public.appointment USING btree (patient_id);


--
-- Name: ix_audit_log_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_log_created ON public.audit_log USING btree (created_at);


--
-- Name: ix_audit_log_patient; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_log_patient ON public.audit_log USING btree (patient_id);


--
-- Name: ix_bed_assignment_admission_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bed_assignment_admission_id ON public.bed_assignment USING btree (admission_id);


--
-- Name: ix_bed_assignment_bed_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bed_assignment_bed_id ON public.bed_assignment USING btree (bed_id);


--
-- Name: ix_bed_room_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bed_room_id ON public.bed USING btree (room_id);


--
-- Name: ix_bed_ward_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bed_ward_id ON public.bed USING btree (ward_id);


--
-- Name: ix_bill_adjustment_bill_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bill_adjustment_bill_id ON public.bill_adjustment USING btree (bill_id);


--
-- Name: ix_care_plan_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_plan_patient_id ON public.care_plan USING btree (patient_id);


--
-- Name: ix_care_task_admission_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_task_admission_id ON public.care_task USING btree (admission_id);


--
-- Name: ix_care_task_due_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_task_due_at ON public.care_task USING btree (due_at);


--
-- Name: ix_care_task_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_care_task_patient_id ON public.care_task USING btree (patient_id);


--
-- Name: ix_clinical_note_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clinical_note_patient_id ON public.clinical_note USING btree (patient_id);


--
-- Name: ix_critical_ack_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_critical_ack_patient_id ON public.critical_ack USING btree (patient_id);


--
-- Name: ix_dispense_event_prescription_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_dispense_event_prescription_id ON public.dispense_event USING btree (prescription_id);


--
-- Name: ix_document_page_document_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_document_page_document_id ON public.document_page USING btree (document_id);


--
-- Name: ix_encounter_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_encounter_patient_id ON public.encounter USING btree (patient_id);


--
-- Name: ix_follow_up_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_follow_up_patient_id ON public.follow_up USING btree (patient_id);


--
-- Name: ix_handover_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_handover_patient_id ON public.handover USING btree (patient_id);


--
-- Name: ix_insurance_claim_bill_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_insurance_claim_bill_id ON public.insurance_claim USING btree (bill_id);


--
-- Name: ix_intake_output_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_intake_output_patient_id ON public.intake_output USING btree (patient_id);


--
-- Name: ix_lab_report_patient_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_lab_report_patient_status ON public.lab_report USING btree (patient_id, status);


--
-- Name: ix_lab_result_lab_report_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_lab_result_lab_report_id ON public.lab_result USING btree (lab_report_id);


--
-- Name: ix_med_reconciliation_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_med_reconciliation_patient_id ON public.med_reconciliation USING btree (patient_id);


--
-- Name: ix_medical_document_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_medical_document_patient_id ON public.medical_document USING btree (patient_id);


--
-- Name: ix_medication_administration_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_medication_administration_patient_id ON public.medication_administration USING btree (patient_id);


--
-- Name: ix_medication_administration_prescription_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_medication_administration_prescription_id ON public.medication_administration USING btree (prescription_id);


--
-- Name: ix_monitoring_device_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_monitoring_device_patient_id ON public.monitoring_device USING btree (patient_id);


--
-- Name: ix_notification_role; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notification_role ON public.notification USING btree (role);


--
-- Name: ix_notification_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notification_user_id ON public.notification USING btree (user_id);


--
-- Name: ix_observation_patient_type_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_observation_patient_type_time ON public.observation USING btree (patient_id, type_code, observed_at);


--
-- Name: ix_patient_assignment_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_patient_assignment_patient_id ON public.patient_assignment USING btree (patient_id);


--
-- Name: ix_patient_assignment_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_patient_assignment_user_id ON public.patient_assignment USING btree (user_id);


--
-- Name: ix_patient_deliverable_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_patient_deliverable_patient_id ON public.patient_deliverable USING btree (patient_id);


--
-- Name: ix_payment_bill_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_payment_bill_id ON public.payment USING btree (bill_id);


--
-- Name: ix_prescription_patient_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_prescription_patient_status ON public.prescription USING btree (patient_id, status);


--
-- Name: ix_problem_patient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_problem_patient_id ON public.problem USING btree (patient_id);


--
-- Name: ix_radiology_patient; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_radiology_patient ON public.radiology_record USING btree (patient_id);


--
-- Name: ix_radiology_report_version_radiology_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_radiology_report_version_radiology_id ON public.radiology_report_version USING btree (radiology_id);


--
-- Name: ix_room_ward_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_room_ward_id ON public.room USING btree (ward_id);


--
-- Name: ix_stock_movement_medicine_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stock_movement_medicine_id ON public.stock_movement USING btree (medicine_id);


--
-- Name: uq_admission_active_patient; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_admission_active_patient ON public.admission USING btree (patient_id) WHERE ((status)::text = 'Admitted'::text);


--
-- Name: uq_alert_open_patient_rule; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_alert_open_patient_rule ON public.alert USING btree (patient_id, rule_id) WHERE ((status)::text <> 'Resolved'::text);


--
-- Name: uq_appointment_doctor_slot_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_appointment_doctor_slot_active ON public.appointment USING btree (doctor_id, appointment_date, appointment_time) WHERE ((status)::text = ANY ((ARRAY['Scheduled'::character varying, 'Checked-in'::character varying])::text[]));


--
-- Name: uq_bed_assignment_open_admission; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_bed_assignment_open_admission ON public.bed_assignment USING btree (admission_id) WHERE (ended_at IS NULL);


--
-- Name: uq_bed_assignment_open_bed; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_bed_assignment_open_bed ON public.bed_assignment USING btree (bed_id) WHERE (ended_at IS NULL);


--
-- Name: uq_patient_assignment_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_patient_assignment_active ON public.patient_assignment USING btree (patient_id, user_id) WHERE active;


--
-- Name: admission fk_admission_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admission
    ADD CONSTRAINT fk_admission_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: admission fk_admission_discharge_authorized_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admission
    ADD CONSTRAINT fk_admission_discharge_authorized_by_id_app_user FOREIGN KEY (discharge_authorized_by_id) REFERENCES public.app_user(id);


--
-- Name: admission fk_admission_encounter_id_encounter; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admission
    ADD CONSTRAINT fk_admission_encounter_id_encounter FOREIGN KEY (encounter_id) REFERENCES public.encounter(id);


--
-- Name: admission fk_admission_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admission
    ADD CONSTRAINT fk_admission_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: admission fk_admission_responsible_doctor_id_doctor; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admission
    ADD CONSTRAINT fk_admission_responsible_doctor_id_doctor FOREIGN KEY (responsible_doctor_id) REFERENCES public.doctor(id);


--
-- Name: ai_conversation fk_ai_conversation_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_conversation
    ADD CONSTRAINT fk_ai_conversation_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: ai_conversation fk_ai_conversation_user_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_conversation
    ADD CONSTRAINT fk_ai_conversation_user_id_app_user FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: ai_message fk_ai_message_conversation_id_ai_conversation; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ai_message
    ADD CONSTRAINT fk_ai_message_conversation_id_ai_conversation FOREIGN KEY (conversation_id) REFERENCES public.ai_conversation(id);


--
-- Name: alert fk_alert_ack_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert
    ADD CONSTRAINT fk_alert_ack_by_id_app_user FOREIGN KEY (ack_by_id) REFERENCES public.app_user(id);


--
-- Name: alert fk_alert_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert
    ADD CONSTRAINT fk_alert_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: alert fk_alert_observation_id_observation; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert
    ADD CONSTRAINT fk_alert_observation_id_observation FOREIGN KEY (observation_id) REFERENCES public.observation(id);


--
-- Name: alert fk_alert_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert
    ADD CONSTRAINT fk_alert_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: alert fk_alert_resolved_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert
    ADD CONSTRAINT fk_alert_resolved_by_id_app_user FOREIGN KEY (resolved_by_id) REFERENCES public.app_user(id);


--
-- Name: alert fk_alert_responder_user_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert
    ADD CONSTRAINT fk_alert_responder_user_id_app_user FOREIGN KEY (responder_user_id) REFERENCES public.app_user(id);


--
-- Name: alert_rule fk_alert_rule_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert_rule
    ADD CONSTRAINT fk_alert_rule_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: alert fk_alert_rule_id_alert_rule; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert
    ADD CONSTRAINT fk_alert_rule_id_alert_rule FOREIGN KEY (rule_id) REFERENCES public.alert_rule(id);


--
-- Name: alert_rule fk_alert_rule_type_code_observation_type; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alert_rule
    ADD CONSTRAINT fk_alert_rule_type_code_observation_type FOREIGN KEY (type_code) REFERENCES public.observation_type(code);


--
-- Name: allergy fk_allergy_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allergy
    ADD CONSTRAINT fk_allergy_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: allergy fk_allergy_recorded_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.allergy
    ADD CONSTRAINT fk_allergy_recorded_by_id_app_user FOREIGN KEY (recorded_by_id) REFERENCES public.app_user(id);


--
-- Name: app_user fk_app_user_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT fk_app_user_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: app_user fk_app_user_doctor_id_doctor; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT fk_app_user_doctor_id_doctor FOREIGN KEY (doctor_id) REFERENCES public.doctor(id);


--
-- Name: app_user fk_app_user_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT fk_app_user_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: app_user fk_app_user_ward_id_ward; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT fk_app_user_ward_id_ward FOREIGN KEY (ward_id) REFERENCES public.ward(id);


--
-- Name: appointment fk_appointment_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointment
    ADD CONSTRAINT fk_appointment_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: appointment fk_appointment_doctor_id_doctor; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointment
    ADD CONSTRAINT fk_appointment_doctor_id_doctor FOREIGN KEY (doctor_id) REFERENCES public.doctor(id);


--
-- Name: appointment fk_appointment_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointment
    ADD CONSTRAINT fk_appointment_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: audit_log fk_audit_log_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT fk_audit_log_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: audit_log fk_audit_log_user_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT fk_audit_log_user_id_app_user FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: bed_assignment fk_bed_assignment_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed_assignment
    ADD CONSTRAINT fk_bed_assignment_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: bed_assignment fk_bed_assignment_bed_id_bed; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed_assignment
    ADD CONSTRAINT fk_bed_assignment_bed_id_bed FOREIGN KEY (bed_id) REFERENCES public.bed(id);


--
-- Name: bed_assignment fk_bed_assignment_moved_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed_assignment
    ADD CONSTRAINT fk_bed_assignment_moved_by_id_app_user FOREIGN KEY (moved_by_id) REFERENCES public.app_user(id);


--
-- Name: bed fk_bed_room_id_room; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed
    ADD CONSTRAINT fk_bed_room_id_room FOREIGN KEY (room_id) REFERENCES public.room(id);


--
-- Name: bed fk_bed_ward_id_ward; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bed
    ADD CONSTRAINT fk_bed_ward_id_ward FOREIGN KEY (ward_id) REFERENCES public.ward(id);


--
-- Name: bill_adjustment fk_bill_adjustment_approved_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill_adjustment
    ADD CONSTRAINT fk_bill_adjustment_approved_by_id_app_user FOREIGN KEY (approved_by_id) REFERENCES public.app_user(id);


--
-- Name: bill_adjustment fk_bill_adjustment_bill_id_bill; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill_adjustment
    ADD CONSTRAINT fk_bill_adjustment_bill_id_bill FOREIGN KEY (bill_id) REFERENCES public.bill(id);


--
-- Name: bill_adjustment fk_bill_adjustment_requested_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill_adjustment
    ADD CONSTRAINT fk_bill_adjustment_requested_by_id_app_user FOREIGN KEY (requested_by_id) REFERENCES public.app_user(id);


--
-- Name: bill fk_bill_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill
    ADD CONSTRAINT fk_bill_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: bill fk_bill_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill
    ADD CONSTRAINT fk_bill_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: bill fk_bill_encounter_id_encounter; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill
    ADD CONSTRAINT fk_bill_encounter_id_encounter FOREIGN KEY (encounter_id) REFERENCES public.encounter(id);


--
-- Name: bill fk_bill_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bill
    ADD CONSTRAINT fk_bill_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: care_plan fk_care_plan_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_plan
    ADD CONSTRAINT fk_care_plan_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: care_plan fk_care_plan_author_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_plan
    ADD CONSTRAINT fk_care_plan_author_id_app_user FOREIGN KEY (author_id) REFERENCES public.app_user(id);


--
-- Name: care_plan fk_care_plan_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_plan
    ADD CONSTRAINT fk_care_plan_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: care_task fk_care_task_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_task
    ADD CONSTRAINT fk_care_task_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: care_task fk_care_task_assigned_user_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_task
    ADD CONSTRAINT fk_care_task_assigned_user_id_app_user FOREIGN KEY (assigned_user_id) REFERENCES public.app_user(id);


--
-- Name: care_task fk_care_task_care_plan_id_care_plan; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_task
    ADD CONSTRAINT fk_care_task_care_plan_id_care_plan FOREIGN KEY (care_plan_id) REFERENCES public.care_plan(id);


--
-- Name: care_task fk_care_task_completed_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_task
    ADD CONSTRAINT fk_care_task_completed_by_id_app_user FOREIGN KEY (completed_by_id) REFERENCES public.app_user(id);


--
-- Name: care_task fk_care_task_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_task
    ADD CONSTRAINT fk_care_task_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: care_task fk_care_task_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.care_task
    ADD CONSTRAINT fk_care_task_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: clinical_note fk_clinical_note_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clinical_note
    ADD CONSTRAINT fk_clinical_note_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: clinical_note fk_clinical_note_amends_note_id_clinical_note; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clinical_note
    ADD CONSTRAINT fk_clinical_note_amends_note_id_clinical_note FOREIGN KEY (amends_note_id) REFERENCES public.clinical_note(id);


--
-- Name: clinical_note fk_clinical_note_author_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clinical_note
    ADD CONSTRAINT fk_clinical_note_author_id_app_user FOREIGN KEY (author_id) REFERENCES public.app_user(id);


--
-- Name: clinical_note fk_clinical_note_encounter_id_encounter; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clinical_note
    ADD CONSTRAINT fk_clinical_note_encounter_id_encounter FOREIGN KEY (encounter_id) REFERENCES public.encounter(id);


--
-- Name: clinical_note fk_clinical_note_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clinical_note
    ADD CONSTRAINT fk_clinical_note_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: critical_ack fk_critical_ack_ack_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.critical_ack
    ADD CONSTRAINT fk_critical_ack_ack_by_id_app_user FOREIGN KEY (ack_by_id) REFERENCES public.app_user(id);


--
-- Name: critical_ack fk_critical_ack_notify_user_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.critical_ack
    ADD CONSTRAINT fk_critical_ack_notify_user_id_app_user FOREIGN KEY (notify_user_id) REFERENCES public.app_user(id);


--
-- Name: critical_ack fk_critical_ack_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.critical_ack
    ADD CONSTRAINT fk_critical_ack_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: dispense_event fk_dispense_event_dispensed_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dispense_event
    ADD CONSTRAINT fk_dispense_event_dispensed_by_id_app_user FOREIGN KEY (dispensed_by_id) REFERENCES public.app_user(id);


--
-- Name: dispense_event fk_dispense_event_medicine_id_medicine; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dispense_event
    ADD CONSTRAINT fk_dispense_event_medicine_id_medicine FOREIGN KEY (medicine_id) REFERENCES public.medicine(id);


--
-- Name: dispense_event fk_dispense_event_prescription_id_prescription; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dispense_event
    ADD CONSTRAINT fk_dispense_event_prescription_id_prescription FOREIGN KEY (prescription_id) REFERENCES public.prescription(id);


--
-- Name: document_page fk_document_page_corrected_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_page
    ADD CONSTRAINT fk_document_page_corrected_by_id_app_user FOREIGN KEY (corrected_by_id) REFERENCES public.app_user(id);


--
-- Name: document_page fk_document_page_document_id_medical_document; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_page
    ADD CONSTRAINT fk_document_page_document_id_medical_document FOREIGN KEY (document_id) REFERENCES public.medical_document(id);


--
-- Name: encounter fk_encounter_appointment_id_appointment; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounter
    ADD CONSTRAINT fk_encounter_appointment_id_appointment FOREIGN KEY (appointment_id) REFERENCES public.appointment(id);


--
-- Name: encounter fk_encounter_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounter
    ADD CONSTRAINT fk_encounter_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: encounter fk_encounter_doctor_id_doctor; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounter
    ADD CONSTRAINT fk_encounter_doctor_id_doctor FOREIGN KEY (doctor_id) REFERENCES public.doctor(id);


--
-- Name: encounter fk_encounter_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.encounter
    ADD CONSTRAINT fk_encounter_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: follow_up fk_follow_up_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follow_up
    ADD CONSTRAINT fk_follow_up_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: follow_up fk_follow_up_appointment_id_appointment; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follow_up
    ADD CONSTRAINT fk_follow_up_appointment_id_appointment FOREIGN KEY (appointment_id) REFERENCES public.appointment(id);


--
-- Name: follow_up fk_follow_up_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follow_up
    ADD CONSTRAINT fk_follow_up_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: follow_up fk_follow_up_encounter_id_encounter; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follow_up
    ADD CONSTRAINT fk_follow_up_encounter_id_encounter FOREIGN KEY (encounter_id) REFERENCES public.encounter(id);


--
-- Name: follow_up fk_follow_up_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.follow_up
    ADD CONSTRAINT fk_follow_up_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: handover fk_handover_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover
    ADD CONSTRAINT fk_handover_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: handover fk_handover_author_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover
    ADD CONSTRAINT fk_handover_author_id_app_user FOREIGN KEY (author_id) REFERENCES public.app_user(id);


--
-- Name: handover fk_handover_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover
    ADD CONSTRAINT fk_handover_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: handover fk_handover_reviewed_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover
    ADD CONSTRAINT fk_handover_reviewed_by_id_app_user FOREIGN KEY (reviewed_by_id) REFERENCES public.app_user(id);


--
-- Name: handover fk_handover_ward_id_ward; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover
    ADD CONSTRAINT fk_handover_ward_id_ward FOREIGN KEY (ward_id) REFERENCES public.ward(id);


--
-- Name: insurance_claim fk_insurance_claim_bill_id_bill; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.insurance_claim
    ADD CONSTRAINT fk_insurance_claim_bill_id_bill FOREIGN KEY (bill_id) REFERENCES public.bill(id);


--
-- Name: insurance_claim fk_insurance_claim_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.insurance_claim
    ADD CONSTRAINT fk_insurance_claim_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: intake_output fk_intake_output_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intake_output
    ADD CONSTRAINT fk_intake_output_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: intake_output fk_intake_output_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intake_output
    ADD CONSTRAINT fk_intake_output_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: intake_output fk_intake_output_recorded_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.intake_output
    ADD CONSTRAINT fk_intake_output_recorded_by_id_app_user FOREIGN KEY (recorded_by_id) REFERENCES public.app_user(id);


--
-- Name: lab_report fk_lab_report_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT fk_lab_report_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: lab_report fk_lab_report_collected_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT fk_lab_report_collected_by_id_app_user FOREIGN KEY (collected_by_id) REFERENCES public.app_user(id);


--
-- Name: lab_report fk_lab_report_encounter_id_encounter; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT fk_lab_report_encounter_id_encounter FOREIGN KEY (encounter_id) REFERENCES public.encounter(id);


--
-- Name: lab_report fk_lab_report_ordered_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT fk_lab_report_ordered_by_id_app_user FOREIGN KEY (ordered_by_id) REFERENCES public.app_user(id);


--
-- Name: lab_report fk_lab_report_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT fk_lab_report_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: lab_report fk_lab_report_released_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT fk_lab_report_released_by_id_app_user FOREIGN KEY (released_by_id) REFERENCES public.app_user(id);


--
-- Name: lab_report fk_lab_report_resulted_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT fk_lab_report_resulted_by_id_app_user FOREIGN KEY (resulted_by_id) REFERENCES public.app_user(id);


--
-- Name: lab_report fk_lab_report_verified_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT fk_lab_report_verified_by_id_app_user FOREIGN KEY (verified_by_id) REFERENCES public.app_user(id);


--
-- Name: lab_result fk_lab_result_entered_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_result
    ADD CONSTRAINT fk_lab_result_entered_by_id_app_user FOREIGN KEY (entered_by_id) REFERENCES public.app_user(id);


--
-- Name: lab_result fk_lab_result_lab_report_id_lab_report; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_result
    ADD CONSTRAINT fk_lab_result_lab_report_id_lab_report FOREIGN KEY (lab_report_id) REFERENCES public.lab_report(id);


--
-- Name: lab_result fk_lab_result_supersedes_id_lab_result; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lab_result
    ADD CONSTRAINT fk_lab_result_supersedes_id_lab_result FOREIGN KEY (supersedes_id) REFERENCES public.lab_result(id);


--
-- Name: med_reconciliation fk_med_reconciliation_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.med_reconciliation
    ADD CONSTRAINT fk_med_reconciliation_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: med_reconciliation fk_med_reconciliation_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.med_reconciliation
    ADD CONSTRAINT fk_med_reconciliation_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: med_reconciliation fk_med_reconciliation_pharmacist_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.med_reconciliation
    ADD CONSTRAINT fk_med_reconciliation_pharmacist_id_app_user FOREIGN KEY (pharmacist_id) REFERENCES public.app_user(id);


--
-- Name: medical_document fk_medical_document_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document
    ADD CONSTRAINT fk_medical_document_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: medical_document fk_medical_document_encounter_id_encounter; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document
    ADD CONSTRAINT fk_medical_document_encounter_id_encounter FOREIGN KEY (encounter_id) REFERENCES public.encounter(id);


--
-- Name: medical_document fk_medical_document_lab_report_id_lab_report; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document
    ADD CONSTRAINT fk_medical_document_lab_report_id_lab_report FOREIGN KEY (lab_report_id) REFERENCES public.lab_report(id);


--
-- Name: medical_document fk_medical_document_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document
    ADD CONSTRAINT fk_medical_document_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: medical_document fk_medical_document_radiology_id_radiology_record; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document
    ADD CONSTRAINT fk_medical_document_radiology_id_radiology_record FOREIGN KEY (radiology_id) REFERENCES public.radiology_record(id);


--
-- Name: medical_document fk_medical_document_reviewed_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document
    ADD CONSTRAINT fk_medical_document_reviewed_by_id_app_user FOREIGN KEY (reviewed_by_id) REFERENCES public.app_user(id);


--
-- Name: medical_document fk_medical_document_supersedes_id_medical_document; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document
    ADD CONSTRAINT fk_medical_document_supersedes_id_medical_document FOREIGN KEY (supersedes_id) REFERENCES public.medical_document(id);


--
-- Name: medical_document fk_medical_document_uploaded_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_document
    ADD CONSTRAINT fk_medical_document_uploaded_by_id_app_user FOREIGN KEY (uploaded_by_id) REFERENCES public.app_user(id);


--
-- Name: medication_administration fk_medication_administration_administered_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medication_administration
    ADD CONSTRAINT fk_medication_administration_administered_by_id_app_user FOREIGN KEY (administered_by_id) REFERENCES public.app_user(id);


--
-- Name: medication_administration fk_medication_administration_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medication_administration
    ADD CONSTRAINT fk_medication_administration_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: medication_administration fk_medication_administration_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medication_administration
    ADD CONSTRAINT fk_medication_administration_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: medication_administration fk_medication_administration_prescription_id_prescription; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medication_administration
    ADD CONSTRAINT fk_medication_administration_prescription_id_prescription FOREIGN KEY (prescription_id) REFERENCES public.prescription(id);


--
-- Name: monitoring_device fk_monitoring_device_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monitoring_device
    ADD CONSTRAINT fk_monitoring_device_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: monitoring_device fk_monitoring_device_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monitoring_device
    ADD CONSTRAINT fk_monitoring_device_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: notification fk_notification_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT fk_notification_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: notification fk_notification_user_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT fk_notification_user_id_app_user FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: observation fk_observation_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT fk_observation_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: observation fk_observation_device_id_monitoring_device; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT fk_observation_device_id_monitoring_device FOREIGN KEY (device_id) REFERENCES public.monitoring_device(id);


--
-- Name: observation fk_observation_encounter_id_encounter; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT fk_observation_encounter_id_encounter FOREIGN KEY (encounter_id) REFERENCES public.encounter(id);


--
-- Name: observation fk_observation_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT fk_observation_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: observation fk_observation_recorded_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT fk_observation_recorded_by_id_app_user FOREIGN KEY (recorded_by_id) REFERENCES public.app_user(id);


--
-- Name: observation fk_observation_supersedes_id_observation; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT fk_observation_supersedes_id_observation FOREIGN KEY (supersedes_id) REFERENCES public.observation(id);


--
-- Name: observation fk_observation_type_code_observation_type; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT fk_observation_type_code_observation_type FOREIGN KEY (type_code) REFERENCES public.observation_type(code);


--
-- Name: patient_assignment fk_patient_assignment_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_assignment
    ADD CONSTRAINT fk_patient_assignment_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: patient_assignment fk_patient_assignment_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_assignment
    ADD CONSTRAINT fk_patient_assignment_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: patient_assignment fk_patient_assignment_user_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_assignment
    ADD CONSTRAINT fk_patient_assignment_user_id_app_user FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: patient_deliverable fk_patient_deliverable_created_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_deliverable
    ADD CONSTRAINT fk_patient_deliverable_created_by_id_app_user FOREIGN KEY (created_by_id) REFERENCES public.app_user(id);


--
-- Name: patient_deliverable fk_patient_deliverable_document_id_medical_document; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_deliverable
    ADD CONSTRAINT fk_patient_deliverable_document_id_medical_document FOREIGN KEY (document_id) REFERENCES public.medical_document(id);


--
-- Name: patient_deliverable fk_patient_deliverable_handed_over_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_deliverable
    ADD CONSTRAINT fk_patient_deliverable_handed_over_by_id_app_user FOREIGN KEY (handed_over_by_id) REFERENCES public.app_user(id);


--
-- Name: patient_deliverable fk_patient_deliverable_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient_deliverable
    ADD CONSTRAINT fk_patient_deliverable_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: patient fk_patient_identity_verified_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.patient
    ADD CONSTRAINT fk_patient_identity_verified_by_id_app_user FOREIGN KEY (identity_verified_by_id) REFERENCES public.app_user(id);


--
-- Name: payment fk_payment_approved_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT fk_payment_approved_by_id_app_user FOREIGN KEY (approved_by_id) REFERENCES public.app_user(id);


--
-- Name: payment fk_payment_bill_id_bill; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT fk_payment_bill_id_bill FOREIGN KEY (bill_id) REFERENCES public.bill(id);


--
-- Name: payment fk_payment_received_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT fk_payment_received_by_id_app_user FOREIGN KEY (received_by_id) REFERENCES public.app_user(id);


--
-- Name: prescription fk_prescription_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT fk_prescription_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: prescription fk_prescription_encounter_id_encounter; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT fk_prescription_encounter_id_encounter FOREIGN KEY (encounter_id) REFERENCES public.encounter(id);


--
-- Name: prescription fk_prescription_medicine_id_medicine; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT fk_prescription_medicine_id_medicine FOREIGN KEY (medicine_id) REFERENCES public.medicine(id);


--
-- Name: prescription fk_prescription_ordered_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT fk_prescription_ordered_by_id_app_user FOREIGN KEY (ordered_by_id) REFERENCES public.app_user(id);


--
-- Name: prescription fk_prescription_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT fk_prescription_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: prescription fk_prescription_verified_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescription
    ADD CONSTRAINT fk_prescription_verified_by_id_app_user FOREIGN KEY (verified_by_id) REFERENCES public.app_user(id);


--
-- Name: problem fk_problem_encounter_id_encounter; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.problem
    ADD CONSTRAINT fk_problem_encounter_id_encounter FOREIGN KEY (encounter_id) REFERENCES public.encounter(id);


--
-- Name: problem fk_problem_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.problem
    ADD CONSTRAINT fk_problem_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: problem fk_problem_recorded_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.problem
    ADD CONSTRAINT fk_problem_recorded_by_id_app_user FOREIGN KEY (recorded_by_id) REFERENCES public.app_user(id);


--
-- Name: radiology_record fk_radiology_record_admission_id_admission; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_record
    ADD CONSTRAINT fk_radiology_record_admission_id_admission FOREIGN KEY (admission_id) REFERENCES public.admission(id);


--
-- Name: radiology_record fk_radiology_record_authorized_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_record
    ADD CONSTRAINT fk_radiology_record_authorized_by_id_app_user FOREIGN KEY (authorized_by_id) REFERENCES public.app_user(id);


--
-- Name: radiology_record fk_radiology_record_encounter_id_encounter; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_record
    ADD CONSTRAINT fk_radiology_record_encounter_id_encounter FOREIGN KEY (encounter_id) REFERENCES public.encounter(id);


--
-- Name: radiology_record fk_radiology_record_ordered_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_record
    ADD CONSTRAINT fk_radiology_record_ordered_by_id_app_user FOREIGN KEY (ordered_by_id) REFERENCES public.app_user(id);


--
-- Name: radiology_record fk_radiology_record_patient_id_patient; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_record
    ADD CONSTRAINT fk_radiology_record_patient_id_patient FOREIGN KEY (patient_id) REFERENCES public.patient(id);


--
-- Name: radiology_record fk_radiology_record_performed_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_record
    ADD CONSTRAINT fk_radiology_record_performed_by_id_app_user FOREIGN KEY (performed_by_id) REFERENCES public.app_user(id);


--
-- Name: radiology_record fk_radiology_record_reported_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_record
    ADD CONSTRAINT fk_radiology_record_reported_by_id_app_user FOREIGN KEY (reported_by_id) REFERENCES public.app_user(id);


--
-- Name: radiology_report_version fk_radiology_report_version_author_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_report_version
    ADD CONSTRAINT fk_radiology_report_version_author_id_app_user FOREIGN KEY (author_id) REFERENCES public.app_user(id);


--
-- Name: radiology_report_version fk_radiology_report_version_radiology_id_radiology_record; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.radiology_report_version
    ADD CONSTRAINT fk_radiology_report_version_radiology_id_radiology_record FOREIGN KEY (radiology_id) REFERENCES public.radiology_record(id);


--
-- Name: room fk_room_ward_id_ward; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.room
    ADD CONSTRAINT fk_room_ward_id_ward FOREIGN KEY (ward_id) REFERENCES public.ward(id);


--
-- Name: stock_movement fk_stock_movement_medicine_id_medicine; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movement
    ADD CONSTRAINT fk_stock_movement_medicine_id_medicine FOREIGN KEY (medicine_id) REFERENCES public.medicine(id);


--
-- Name: stock_movement fk_stock_movement_user_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movement
    ADD CONSTRAINT fk_stock_movement_user_id_app_user FOREIGN KEY (user_id) REFERENCES public.app_user(id);


--
-- Name: system_setting fk_system_setting_updated_by_id_app_user; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_setting
    ADD CONSTRAINT fk_system_setting_updated_by_id_app_user FOREIGN KEY (updated_by_id) REFERENCES public.app_user(id);


--
-- Name: ward fk_ward_department_id_department; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ward
    ADD CONSTRAINT fk_ward_department_id_department FOREIGN KEY (department_id) REFERENCES public.department(id);


--
-- PostgreSQL database dump complete
--

\unrestrict b0tMjCJuhbVpX8afBDvSl2z3bI0DmP4KmBMFwZA3OiKuZZnHx7vHQTgKXneokFH

