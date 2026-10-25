SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

INSERT INTO public.patient_deliverable (id, patient_id, kind, title, ref_type, ref_id, document_id, digital_available, physical_status, physical_note, received_by_name, handed_over_at, handed_over_by_id, created_by_id, created_at, updated_at) VALUES
	(401, 153, 'Laboratory report', 'Complete blood count (2026-10-20)', 'lab', 211, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.173089+00', '2026-10-25 15:05:16.174213+00'),
	(402, 153, 'Invoice / receipt', 'Outpatient bill', 'bill', 149, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.178474+00', '2026-10-25 15:05:16.17853+00'),
	(403, 154, 'Discharge summary', 'Discharge summary - Paediatric Ward (2026-10-13 to 2026-10-25)', 'admission', 76, NULL, true, 'Ready for collection', '', '', NULL, NULL, 14, '2026-10-25 15:05:16.205847+00', '2026-10-25 15:05:16.207753+00'),
	(404, 154, 'Laboratory report', 'Complete blood count (2026-10-15)', 'lab', 212, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.212044+00', '2026-10-25 15:05:16.213164+00'),
	(405, 154, 'Radiology report', 'X-ray Chest, PA', 'radiology', 57, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:16.216117+00', '2026-10-25 15:05:16.21612+00'),
	(406, 154, 'Invoice / receipt', 'Inpatient bill', 'bill', 150, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.220328+00', '2026-10-25 15:05:16.220331+00'),
	(407, 155, 'Laboratory report', 'Complete blood count (2026-10-25)', 'lab', 213, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.249034+00', '2026-10-25 15:05:16.250637+00'),
	(408, 155, 'Invoice / receipt', 'Inpatient bill', 'bill', 151, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.256509+00', '2026-10-25 15:05:16.256512+00'),
	(409, 156, 'Laboratory report', 'Complete blood count (2026-10-19)', 'lab', 214, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.265896+00', '2026-10-25 15:05:16.266708+00'),
	(410, 156, 'Laboratory report', 'Blood glucose (2026-10-16)', 'lab', 215, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.270867+00', '2026-10-25 15:05:16.271686+00'),
	(411, 156, 'Radiology report', 'Ultrasound Abdomen', 'radiology', 58, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:16.274281+00', '2026-10-25 15:05:16.274284+00'),
	(412, 156, 'Invoice / receipt', 'Outpatient bill', 'bill', 152, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.278778+00', '2026-10-25 15:05:16.278781+00'),
	(413, 157, 'Laboratory report', 'Complete blood count (2026-10-21)', 'lab', 216, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.286711+00', '2026-10-25 15:05:16.287556+00'),
	(414, 157, 'Radiology report', 'X-ray Chest, PA', 'radiology', 59, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:16.290842+00', '2026-10-25 15:05:16.290845+00'),
	(415, 157, 'Invoice / receipt', 'Outpatient bill', 'bill', 153, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.296024+00', '2026-10-25 15:05:16.296028+00'),
	(416, 158, 'Laboratory report', 'Complete blood count (2026-10-17)', 'lab', 217, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.304294+00', '2026-10-25 15:05:16.305004+00'),
	(417, 158, 'Radiology report', 'X-ray Knee, AP/lateral', 'radiology', 60, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:16.307216+00', '2026-10-25 15:05:16.307218+00'),
	(418, 158, 'Invoice / receipt', 'Outpatient bill', 'bill', 154, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.31157+00', '2026-10-25 15:05:16.311574+00'),
	(419, 159, 'Laboratory report', 'Liver function (2026-10-25)', 'lab', 218, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.31914+00', '2026-10-25 15:05:16.320045+00'),
	(420, 159, 'Radiology report', 'Ultrasound Abdomen', 'radiology', 61, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:16.322388+00', '2026-10-25 15:05:16.322391+00'),
	(421, 159, 'Invoice / receipt', 'Outpatient bill', 'bill', 155, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.32784+00', '2026-10-25 15:05:16.327843+00'),
	(422, 160, 'Laboratory report', 'Complete blood count (2026-10-15)', 'lab', 219, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.336587+00', '2026-10-25 15:05:16.33659+00'),
	(423, 160, 'Invoice / receipt', 'Outpatient bill', 'bill', 156, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.342109+00', '2026-10-25 15:05:16.342112+00'),
	(424, 161, 'Laboratory report', 'Complete blood count (2026-10-17)', 'lab', 220, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.350621+00', '2026-10-25 15:05:16.350624+00'),
	(425, 161, 'Radiology report', 'X-ray Chest, PA', 'radiology', 62, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:16.353123+00', '2026-10-25 15:05:16.353126+00'),
	(426, 161, 'Invoice / receipt', 'Outpatient bill', 'bill', 157, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.357598+00', '2026-10-25 15:05:16.357601+00'),
	(427, 162, 'Laboratory report', 'Complete blood count (2026-10-19)', 'lab', 221, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.365422+00', '2026-10-25 15:05:16.36672+00'),
	(428, 162, 'Invoice / receipt', 'Outpatient bill', 'bill', 158, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.37094+00', '2026-10-25 15:05:16.370943+00'),
	(429, 163, 'Laboratory report', 'Lipid profile (2026-10-17)', 'lab', 222, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.37871+00', '2026-10-25 15:05:16.379439+00'),
	(430, 163, 'Laboratory report', 'Complete blood count (2026-10-20)', 'lab', 223, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.383343+00', '2026-10-25 15:05:16.384532+00'),
	(431, 163, 'Invoice / receipt', 'Outpatient bill', 'bill', 159, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.387536+00', '2026-10-25 15:05:16.387539+00'),
	(432, 164, 'Discharge summary', 'Discharge summary - Orthopaedic Ward (2026-10-18 to 2026-10-25)', 'admission', 78, NULL, true, 'Ready for collection', '', '', NULL, NULL, 15, '2026-10-25 15:05:16.415906+00', '2026-10-25 15:05:16.418331+00'),
	(433, 164, 'Laboratory report', 'Complete blood count (2026-10-18)', 'lab', 224, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.422716+00', '2026-10-25 15:05:16.422719+00'),
	(434, 164, 'Radiology report', 'Ultrasound Abdomen', 'radiology', 63, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:16.426746+00', '2026-10-25 15:05:16.426749+00'),
	(435, 164, 'Invoice / receipt', 'Inpatient bill', 'bill', 160, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.432018+00', '2026-10-25 15:05:16.432021+00'),
	(436, 165, 'Laboratory report', 'Complete blood count (2026-10-15)', 'lab', 226, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.440504+00', '2026-10-25 15:05:16.441693+00'),
	(437, 165, 'Invoice / receipt', 'Outpatient bill', 'bill', 161, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.445764+00', '2026-10-25 15:05:16.445767+00'),
	(438, 166, 'Invoice / receipt', 'Outpatient bill', 'bill', 162, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.454775+00', '2026-10-25 15:05:16.454778+00'),
	(439, 167, 'Laboratory report', 'Renal function (2026-10-18)', 'lab', 228, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.46305+00', '2026-10-25 15:05:16.463757+00'),
	(440, 167, 'Laboratory report', 'Complete blood count (2026-10-17)', 'lab', 229, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.467994+00', '2026-10-25 15:05:16.469224+00'),
	(441, 167, 'Invoice / receipt', 'Outpatient bill', 'bill', 163, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.473532+00', '2026-10-25 15:05:16.473535+00'),
	(442, 168, 'Laboratory report', 'Thyroid panel (2026-10-24)', 'lab', 230, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.479621+00', '2026-10-25 15:05:16.480786+00'),
	(443, 168, 'Invoice / receipt', 'Outpatient bill', 'bill', 164, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.484796+00', '2026-10-25 15:05:16.484799+00'),
	(444, 169, 'Laboratory report', 'Renal function (2026-10-18)', 'lab', 231, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.490734+00', '2026-10-25 15:05:16.491317+00'),
	(445, 169, 'Invoice / receipt', 'Outpatient bill', 'bill', 165, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.497128+00', '2026-10-25 15:05:16.497131+00'),
	(446, 170, 'Invoice / receipt', 'Outpatient bill', 'bill', 166, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.506369+00', '2026-10-25 15:05:16.506371+00'),
	(447, 171, 'Laboratory report', 'Lipid profile (2026-10-15)', 'lab', 234, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.513566+00', '2026-10-25 15:05:16.514785+00'),
	(448, 171, 'Invoice / receipt', 'Outpatient bill', 'bill', 167, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.518446+00', '2026-10-25 15:05:16.518449+00'),
	(449, 172, 'Laboratory report', 'Complete blood count (2026-10-24)', 'lab', 235, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.525292+00', '2026-10-25 15:05:16.52717+00'),
	(450, 172, 'Invoice / receipt', 'Outpatient bill', 'bill', 168, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.532198+00', '2026-10-25 15:05:16.5322+00'),
	(451, 173, 'Discharge summary', 'Discharge summary - Orthopaedic Ward (2026-10-13 to 2026-10-25)', 'admission', 79, NULL, true, 'Ready for collection', '', '', NULL, NULL, 13, '2026-10-25 15:05:16.56032+00', '2026-10-25 15:05:16.562039+00'),
	(452, 173, 'Radiology report', 'X-ray Knee, AP/lateral', 'radiology', 64, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:16.565899+00', '2026-10-25 15:05:16.565902+00'),
	(453, 173, 'Invoice / receipt', 'Inpatient bill', 'bill', 169, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.571274+00', '2026-10-25 15:05:16.571278+00'),
	(454, 174, 'Invoice / receipt', 'Outpatient bill', 'bill', 170, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.580815+00', '2026-10-25 15:05:16.580818+00'),
	(455, 175, 'Invoice / receipt', 'Outpatient bill', 'bill', 171, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.589486+00', '2026-10-25 15:05:16.589489+00'),
	(456, 176, 'Laboratory report', 'Renal function (2026-10-21)', 'lab', 239, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.597368+00', '2026-10-25 15:05:16.597371+00'),
	(457, 176, 'Laboratory report', 'Complete blood count (2026-10-21)', 'lab', 240, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.602198+00', '2026-10-25 15:05:16.6022+00'),
	(458, 176, 'Invoice / receipt', 'Outpatient bill', 'bill', 172, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.607384+00', '2026-10-25 15:05:16.607387+00'),
	(459, 177, 'Laboratory report', 'Lipid profile (2026-10-21)', 'lab', 241, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.632904+00', '2026-10-25 15:05:16.633525+00'),
	(460, 177, 'Laboratory report', 'Complete blood count (2026-10-15)', 'lab', 242, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.637236+00', '2026-10-25 15:05:16.638489+00'),
	(461, 177, 'Invoice / receipt', 'Inpatient bill', 'bill', 173, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.641631+00', '2026-10-25 15:05:16.641633+00'),
	(462, 178, 'Laboratory report', 'Thyroid panel (2026-10-15)', 'lab', 243, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.648719+00', '2026-10-25 15:05:16.649844+00'),
	(463, 178, 'Invoice / receipt', 'Outpatient bill', 'bill', 174, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.654285+00', '2026-10-25 15:05:16.654288+00'),
	(464, 179, 'Laboratory report', 'Complete blood count (2026-10-20)', 'lab', 244, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.661189+00', '2026-10-25 15:05:16.662756+00'),
	(465, 179, 'Invoice / receipt', 'Outpatient bill', 'bill', 175, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.665853+00', '2026-10-25 15:05:16.665856+00'),
	(466, 180, 'Laboratory report', 'Complete blood count (2026-10-22)', 'lab', 245, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.673544+00', '2026-10-25 15:05:16.674679+00'),
	(467, 180, 'Invoice / receipt', 'Outpatient bill', 'bill', 176, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.678664+00', '2026-10-25 15:05:16.678667+00'),
	(468, 181, 'Discharge summary', 'Discharge summary - Maternity Ward (2026-10-20 to 2026-10-25)', 'admission', 81, NULL, true, 'Ready for collection', '', '', NULL, NULL, 16, '2026-10-25 15:05:16.712632+00', '2026-10-25 15:05:16.71459+00'),
	(469, 181, 'Laboratory report', 'Complete blood count (2026-10-15)', 'lab', 246, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.720113+00', '2026-10-25 15:05:16.720867+00'),
	(470, 181, 'Laboratory report', 'Blood glucose (2026-10-22)', 'lab', 247, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.725726+00', '2026-10-25 15:05:16.726522+00'),
	(471, 181, 'Radiology report', 'Ultrasound Abdomen', 'radiology', 65, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:16.728803+00', '2026-10-25 15:05:16.728806+00'),
	(472, 181, 'Invoice / receipt', 'Inpatient bill', 'bill', 177, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.734876+00', '2026-10-25 15:05:16.734879+00'),
	(473, 182, 'Invoice / receipt', 'Outpatient bill', 'bill', 178, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.749762+00', '2026-10-25 15:05:16.749765+00'),
	(474, 183, 'Laboratory report', 'Renal function (2026-10-23)', 'lab', 249, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.763037+00', '2026-10-25 15:05:16.765475+00'),
	(475, 183, 'Invoice / receipt', 'Outpatient bill', 'bill', 179, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.775012+00', '2026-10-25 15:05:16.775019+00'),
	(476, 184, 'Laboratory report', 'Renal function (2026-10-20)', 'lab', 250, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.790025+00', '2026-10-25 15:05:16.792146+00'),
	(477, 184, 'Invoice / receipt', 'Outpatient bill', 'bill', 180, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.800429+00', '2026-10-25 15:05:16.800432+00'),
	(478, 185, 'Laboratory report', 'Thyroid panel (2026-10-25)', 'lab', 251, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.815375+00', '2026-10-25 15:05:16.817504+00'),
	(479, 185, 'Invoice / receipt', 'Outpatient bill', 'bill', 181, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.825621+00', '2026-10-25 15:05:16.825625+00'),
	(480, 186, 'Laboratory report', 'Complete blood count (2026-10-19)', 'lab', 252, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.842174+00', '2026-10-25 15:05:16.844439+00'),
	(481, 186, 'Invoice / receipt', 'Outpatient bill', 'bill', 182, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.853081+00', '2026-10-25 15:05:16.853085+00'),
	(482, 187, 'Laboratory report', 'Renal function (2026-10-18)', 'lab', 253, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.866628+00', '2026-10-25 15:05:16.867848+00'),
	(483, 187, 'Laboratory report', 'Complete blood count (2026-10-23)', 'lab', 254, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.874836+00', '2026-10-25 15:05:16.874841+00'),
	(484, 187, 'Invoice / receipt', 'Outpatient bill', 'bill', 183, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.884508+00', '2026-10-25 15:05:16.884511+00'),
	(485, 188, 'Laboratory report', 'Complete blood count (2026-10-25)', 'lab', 255, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.897491+00', '2026-10-25 15:05:16.897494+00'),
	(486, 188, 'Laboratory report', 'Liver function (2026-10-23)', 'lab', 256, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.905445+00', '2026-10-25 15:05:16.907544+00'),
	(487, 188, 'Invoice / receipt', 'Outpatient bill', 'bill', 184, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.915804+00', '2026-10-25 15:05:16.91581+00'),
	(488, 189, 'Laboratory report', 'Thyroid panel (2026-10-18)', 'lab', 257, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.929475+00', '2026-10-25 15:05:16.931613+00'),
	(489, 189, 'Invoice / receipt', 'Outpatient bill', 'bill', 185, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.93872+00', '2026-10-25 15:05:16.938723+00'),
	(490, 190, 'Laboratory report', 'Renal function (2026-10-16)', 'lab', 258, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.951601+00', '2026-10-25 15:05:16.952616+00'),
	(491, 190, 'Laboratory report', 'Complete blood count (2026-10-18)', 'lab', 259, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:16.959303+00', '2026-10-25 15:05:16.961381+00'),
	(492, 190, 'Invoice / receipt', 'Outpatient bill', 'bill', 186, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:16.968755+00', '2026-10-25 15:05:16.968758+00'),
	(493, 191, 'Discharge summary', 'Discharge summary - High Dependency Unit (2026-10-21 to 2026-10-25)', 'admission', 82, NULL, true, 'Ready for collection', '', '', NULL, NULL, 12, '2026-10-25 15:05:17.020707+00', '2026-10-25 15:05:17.02384+00'),
	(494, 191, 'Laboratory report', 'Lipid profile (2026-10-25)', 'lab', 260, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.031316+00', '2026-10-25 15:05:17.03132+00'),
	(495, 191, 'Laboratory report', 'Complete blood count (2026-10-22)', 'lab', 261, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.039932+00', '2026-10-25 15:05:17.0412+00'),
	(496, 191, 'Radiology report', 'X-ray Chest, PA', 'radiology', 66, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:17.045819+00', '2026-10-25 15:05:17.045823+00'),
	(497, 191, 'Invoice / receipt', 'Inpatient bill', 'bill', 187, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.056156+00', '2026-10-25 15:05:17.05616+00'),
	(498, 192, 'Laboratory report', 'Complete blood count (2026-10-20)', 'lab', 262, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.070206+00', '2026-10-25 15:05:17.101509+00'),
	(499, 192, 'Radiology report', 'Ultrasound Abdomen', 'radiology', 67, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:17.10547+00', '2026-10-25 15:05:17.105473+00'),
	(500, 192, 'Invoice / receipt', 'Outpatient bill', 'bill', 188, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.111227+00', '2026-10-25 15:05:17.11123+00');
INSERT INTO public.patient_deliverable (id, patient_id, kind, title, ref_type, ref_id, document_id, digital_available, physical_status, physical_note, received_by_name, handed_over_at, handed_over_by_id, created_by_id, created_at, updated_at) VALUES
	(501, 193, 'Laboratory report', 'Complete blood count (2026-10-20)', 'lab', 263, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.12212+00', '2026-10-25 15:05:17.122864+00'),
	(502, 193, 'Laboratory report', 'Liver function (2026-10-21)', 'lab', 264, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.127593+00', '2026-10-25 15:05:17.12921+00'),
	(503, 193, 'Invoice / receipt', 'Outpatient bill', 'bill', 189, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.136529+00', '2026-10-25 15:05:17.136532+00'),
	(504, 194, 'Laboratory report', 'Blood glucose (2026-10-24)', 'lab', 265, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.168973+00', '2026-10-25 15:05:17.168977+00'),
	(505, 194, 'Invoice / receipt', 'Inpatient bill', 'bill', 190, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.179829+00', '2026-10-25 15:05:17.179832+00'),
	(506, 195, 'Laboratory report', 'Complete blood count (2026-10-19)', 'lab', 267, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.190197+00', '2026-10-25 15:05:17.190201+00'),
	(507, 195, 'Invoice / receipt', 'Outpatient bill', 'bill', 191, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.197893+00', '2026-10-25 15:05:17.197897+00'),
	(508, 196, 'Laboratory report', 'Thyroid panel (2026-10-19)', 'lab', 268, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.209978+00', '2026-10-25 15:05:17.209981+00'),
	(509, 196, 'Invoice / receipt', 'Outpatient bill', 'bill', 192, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.215815+00', '2026-10-25 15:05:17.215819+00'),
	(510, 197, 'Discharge summary', 'Discharge summary - High Dependency Unit (2026-10-14 to 2026-10-25)', 'admission', 84, NULL, true, 'Ready for collection', '', '', NULL, NULL, 12, '2026-10-25 15:05:17.293523+00', '2026-10-25 15:05:17.295961+00'),
	(511, 197, 'Laboratory report', 'Blood glucose (2026-10-15)', 'lab', 269, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.3007+00', '2026-10-25 15:05:17.301712+00'),
	(512, 197, 'Laboratory report', 'Renal function (2026-10-19)', 'lab', 270, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.306532+00', '2026-10-25 15:05:17.306535+00'),
	(513, 197, 'Invoice / receipt', 'Inpatient bill', 'bill', 193, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.313727+00', '2026-10-25 15:05:17.31373+00'),
	(514, 198, 'Laboratory report', 'Complete blood count (2026-10-16)', 'lab', 271, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.321376+00', '2026-10-25 15:05:17.322+00'),
	(515, 198, 'Laboratory report', 'Liver function (2026-10-21)', 'lab', 272, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.3266+00', '2026-10-25 15:05:17.328087+00'),
	(516, 198, 'Invoice / receipt', 'Outpatient bill', 'bill', 194, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.333817+00', '2026-10-25 15:05:17.33382+00'),
	(517, 199, 'Discharge summary', 'Discharge summary - Orthopaedic Ward (2026-10-18 to 2026-10-25)', 'admission', 85, NULL, true, 'Ready for collection', '', '', NULL, NULL, 13, '2026-10-25 15:05:17.366072+00', '2026-10-25 15:05:17.368006+00'),
	(518, 199, 'Laboratory report', 'Complete blood count (2026-10-23)', 'lab', 273, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.372486+00', '2026-10-25 15:05:17.373247+00'),
	(519, 199, 'Radiology report', 'X-ray Knee, AP/lateral', 'radiology', 68, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:17.375478+00', '2026-10-25 15:05:17.375481+00'),
	(520, 199, 'Invoice / receipt', 'Inpatient bill', 'bill', 195, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.380086+00', '2026-10-25 15:05:17.380088+00'),
	(521, 200, 'Laboratory report', 'Complete blood count (2026-10-16)', 'lab', 274, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.388096+00', '2026-10-25 15:05:17.38878+00'),
	(522, 200, 'Radiology report', 'X-ray Chest, PA', 'radiology', 69, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:17.391132+00', '2026-10-25 15:05:17.391134+00'),
	(523, 200, 'Invoice / receipt', 'Outpatient bill', 'bill', 196, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.395958+00', '2026-10-25 15:05:17.395961+00'),
	(524, 201, 'Laboratory report', 'Liver function (2026-10-17)', 'lab', 275, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.402958+00', '2026-10-25 15:05:17.402961+00'),
	(525, 201, 'Invoice / receipt', 'Outpatient bill', 'bill', 197, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.410944+00', '2026-10-25 15:05:17.410947+00'),
	(526, 202, 'Discharge summary', 'Discharge summary - High Dependency Unit (2026-10-16 to 2026-10-25)', 'admission', 86, NULL, true, 'Ready for collection', '', '', NULL, NULL, 12, '2026-10-25 15:05:17.451757+00', '2026-10-25 15:05:17.453954+00'),
	(527, 202, 'Invoice / receipt', 'Inpatient bill', 'bill', 198, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.464732+00', '2026-10-25 15:05:17.464736+00'),
	(528, 203, 'Laboratory report', 'Complete blood count (2026-10-21)', 'lab', 277, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.480419+00', '2026-10-25 15:05:17.480422+00'),
	(529, 203, 'Radiology report', 'CT Head, plain', 'radiology', 70, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:17.483635+00', '2026-10-25 15:05:17.483638+00'),
	(530, 203, 'Invoice / receipt', 'Outpatient bill', 'bill', 199, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.489128+00', '2026-10-25 15:05:17.489132+00'),
	(531, 204, 'Laboratory report', 'Thyroid panel (2026-10-24)', 'lab', 278, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.501513+00', '2026-10-25 15:05:17.503169+00'),
	(532, 204, 'Invoice / receipt', 'Outpatient bill', 'bill', 200, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.511091+00', '2026-10-25 15:05:17.511095+00'),
	(533, 205, 'Laboratory report', 'Complete blood count (2026-10-15)', 'lab', 279, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.521998+00', '2026-10-25 15:05:17.523775+00'),
	(534, 205, 'Invoice / receipt', 'Outpatient bill', 'bill', 201, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.531766+00', '2026-10-25 15:05:17.53177+00'),
	(535, 206, 'Laboratory report', 'Complete blood count (2026-10-17)', 'lab', 281, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.543187+00', '2026-10-25 15:05:17.543191+00'),
	(536, 206, 'Invoice / receipt', 'Outpatient bill', 'bill', 202, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.552314+00', '2026-10-25 15:05:17.552317+00'),
	(537, 207, 'Laboratory report', 'Blood glucose (2026-10-17)', 'lab', 282, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.592736+00', '2026-10-25 15:05:17.592739+00'),
	(538, 207, 'Laboratory report', 'Renal function (2026-10-20)', 'lab', 283, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.599104+00', '2026-10-25 15:05:17.601138+00'),
	(539, 207, 'Invoice / receipt', 'Inpatient bill', 'bill', 203, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.607706+00', '2026-10-25 15:05:17.607709+00'),
	(540, 208, 'Laboratory report', 'Lipid profile (2026-10-23)', 'lab', 284, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.64989+00', '2026-10-25 15:05:17.652043+00'),
	(541, 208, 'Invoice / receipt', 'Inpatient bill', 'bill', 204, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.659698+00', '2026-10-25 15:05:17.659701+00'),
	(542, 209, 'Laboratory report', 'Complete blood count (2026-10-15)', 'lab', 285, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.672235+00', '2026-10-25 15:05:17.674626+00'),
	(543, 209, 'Invoice / receipt', 'Outpatient bill', 'bill', 205, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.682479+00', '2026-10-25 15:05:17.682483+00'),
	(544, 210, 'Laboratory report', 'Complete blood count (2026-10-16)', 'lab', 286, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.693872+00', '2026-10-25 15:05:17.69578+00'),
	(545, 210, 'Invoice / receipt', 'Outpatient bill', 'bill', 206, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.703638+00', '2026-10-25 15:05:17.703641+00'),
	(546, 211, 'Laboratory report', 'Lipid profile (2026-10-22)', 'lab', 287, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.74274+00', '2026-10-25 15:05:17.74395+00'),
	(547, 211, 'Laboratory report', 'Complete blood count (2026-10-17)', 'lab', 288, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.750017+00', '2026-10-25 15:05:17.750987+00'),
	(548, 211, 'Radiology report', 'X-ray Chest, PA', 'radiology', 71, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:17.754778+00', '2026-10-25 15:05:17.754782+00'),
	(549, 211, 'Invoice / receipt', 'Inpatient bill', 'bill', 207, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.763077+00', '2026-10-25 15:05:17.763081+00'),
	(550, 212, 'Invoice / receipt', 'Outpatient bill', 'bill', 208, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.775895+00', '2026-10-25 15:05:17.775898+00'),
	(551, 213, 'Laboratory report', 'Complete blood count (2026-10-24)', 'lab', 290, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.787607+00', '2026-10-25 15:05:17.789458+00'),
	(552, 213, 'Invoice / receipt', 'Outpatient bill', 'bill', 209, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.795606+00', '2026-10-25 15:05:17.795609+00'),
	(553, 214, 'Discharge summary', 'Discharge summary - High Dependency Unit (2026-10-14 to 2026-10-25)', 'admission', 90, NULL, true, 'Ready for collection', '', '', NULL, NULL, 12, '2026-10-25 15:05:17.836559+00', '2026-10-25 15:05:17.838677+00'),
	(554, 214, 'Laboratory report', 'Lipid profile (2026-10-21)', 'lab', 291, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.8454+00', '2026-10-25 15:05:17.84746+00'),
	(555, 214, 'Invoice / receipt', 'Inpatient bill', 'bill', 210, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.8551+00', '2026-10-25 15:05:17.855104+00'),
	(556, 215, 'Laboratory report', 'Renal function (2026-10-18)', 'lab', 292, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.868801+00', '2026-10-25 15:05:17.869933+00'),
	(557, 215, 'Invoice / receipt', 'Outpatient bill', 'bill', 211, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.880805+00', '2026-10-25 15:05:17.880808+00'),
	(558, 216, 'Laboratory report', 'Renal function (2026-10-17)', 'lab', 294, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.893308+00', '2026-10-25 15:05:17.893312+00'),
	(559, 216, 'Laboratory report', 'Complete blood count (2026-10-22)', 'lab', 295, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.90005+00', '2026-10-25 15:05:17.902195+00'),
	(560, 216, 'Invoice / receipt', 'Outpatient bill', 'bill', 212, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.909778+00', '2026-10-25 15:05:17.909782+00'),
	(561, 217, 'Discharge summary', 'Discharge summary - High Dependency Unit (2026-10-22 to 2026-10-25)', 'admission', 91, NULL, true, 'Ready for collection', '', '', NULL, NULL, 12, '2026-10-25 15:05:17.959847+00', '2026-10-25 15:05:17.962936+00'),
	(562, 217, 'Laboratory report', 'Lipid profile (2026-10-24)', 'lab', 296, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.970246+00', '2026-10-25 15:05:17.971358+00'),
	(563, 217, 'Laboratory report', 'Complete blood count (2026-10-18)', 'lab', 297, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:17.978418+00', '2026-10-25 15:05:17.978422+00'),
	(564, 217, 'Invoice / receipt', 'Inpatient bill', 'bill', 213, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:17.987666+00', '2026-10-25 15:05:17.987669+00'),
	(565, 218, 'Radiology report', 'CT Head, plain', 'radiology', 72, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:17.997688+00', '2026-10-25 15:05:17.997691+00'),
	(566, 218, 'Invoice / receipt', 'Outpatient bill', 'bill', 214, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.004582+00', '2026-10-25 15:05:18.004585+00'),
	(567, 219, 'Laboratory report', 'Complete blood count (2026-10-16)', 'lab', 299, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.014193+00', '2026-10-25 15:05:18.014196+00'),
	(568, 219, 'Radiology report', 'CT Head, plain', 'radiology', 73, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.018952+00', '2026-10-25 15:05:18.018955+00'),
	(569, 219, 'Invoice / receipt', 'Outpatient bill', 'bill', 215, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.026513+00', '2026-10-25 15:05:18.026517+00'),
	(570, 220, 'Laboratory report', 'Thyroid panel (2026-10-18)', 'lab', 300, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.036315+00', '2026-10-25 15:05:18.037758+00'),
	(571, 220, 'Invoice / receipt', 'Outpatient bill', 'bill', 216, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.043656+00', '2026-10-25 15:05:18.043659+00'),
	(572, 221, 'Laboratory report', 'Thyroid panel (2026-10-19)', 'lab', 301, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.051334+00', '2026-10-25 15:05:18.052613+00'),
	(573, 221, 'Invoice / receipt', 'Outpatient bill', 'bill', 217, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.06263+00', '2026-10-25 15:05:18.062634+00'),
	(574, 222, 'Laboratory report', 'Renal function (2026-10-18)', 'lab', 302, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.073925+00', '2026-10-25 15:05:18.073929+00'),
	(575, 222, 'Laboratory report', 'Complete blood count (2026-10-16)', 'lab', 303, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.08085+00', '2026-10-25 15:05:18.082799+00'),
	(576, 222, 'Invoice / receipt', 'Outpatient bill', 'bill', 218, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.090146+00', '2026-10-25 15:05:18.09015+00'),
	(577, 223, 'Discharge summary', 'Discharge summary - High Dependency Unit (2026-10-16 to 2026-10-25)', 'admission', 92, NULL, true, 'Ready for collection', '', '', NULL, NULL, 12, '2026-10-25 15:05:18.134234+00', '2026-10-25 15:05:18.136714+00'),
	(578, 223, 'Laboratory report', 'Lipid profile (2026-10-23)', 'lab', 304, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.14287+00', '2026-10-25 15:05:18.142873+00'),
	(579, 223, 'Laboratory report', 'Renal function (2026-10-25)', 'lab', 305, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.149055+00', '2026-10-25 15:05:18.15116+00'),
	(580, 223, 'Invoice / receipt', 'Inpatient bill', 'bill', 219, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.155538+00', '2026-10-25 15:05:18.155541+00'),
	(581, 224, 'Laboratory report', 'Thyroid panel (2026-10-25)', 'lab', 306, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.162924+00', '2026-10-25 15:05:18.164365+00'),
	(582, 224, 'Invoice / receipt', 'Outpatient bill', 'bill', 220, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.16948+00', '2026-10-25 15:05:18.169483+00'),
	(583, 225, 'Laboratory report', 'Renal function (2026-10-25)', 'lab', 307, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.199969+00', '2026-10-25 15:05:18.200743+00'),
	(584, 225, 'Laboratory report', 'Complete blood count (2026-10-21)', 'lab', 308, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.205383+00', '2026-10-25 15:05:18.20631+00'),
	(585, 225, 'Radiology report', 'X-ray Chest, PA', 'radiology', 74, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.209359+00', '2026-10-25 15:05:18.209362+00'),
	(586, 225, 'Invoice / receipt', 'Inpatient bill', 'bill', 221, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.215109+00', '2026-10-25 15:05:18.215112+00'),
	(587, 226, 'Invoice / receipt', 'Outpatient bill', 'bill', 222, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.227098+00', '2026-10-25 15:05:18.2271+00'),
	(588, 227, 'Laboratory report', 'Complete blood count (2026-10-19)', 'lab', 310, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.235345+00', '2026-10-25 15:05:18.23673+00'),
	(589, 227, 'Invoice / receipt', 'Outpatient bill', 'bill', 223, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.241893+00', '2026-10-25 15:05:18.241895+00'),
	(590, 228, 'Laboratory report', 'Complete blood count (2026-10-20)', 'lab', 311, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.249625+00', '2026-10-25 15:05:18.249628+00'),
	(591, 228, 'Invoice / receipt', 'Outpatient bill', 'bill', 224, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.256182+00', '2026-10-25 15:05:18.256185+00'),
	(592, 229, 'Laboratory report', 'Lipid profile (2026-10-22)', 'lab', 312, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.264487+00', '2026-10-25 15:05:18.265227+00'),
	(593, 229, 'Laboratory report', 'Complete blood count (2026-10-25)', 'lab', 313, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.269935+00', '2026-10-25 15:05:18.269938+00'),
	(594, 229, 'Radiology report', 'X-ray Chest, PA', 'radiology', 75, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.273388+00', '2026-10-25 15:05:18.273391+00'),
	(595, 229, 'Invoice / receipt', 'Outpatient bill', 'bill', 225, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.281154+00', '2026-10-25 15:05:18.281158+00'),
	(596, 230, 'Laboratory report', 'Liver function (2026-10-15)', 'lab', 315, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.293426+00', '2026-10-25 15:05:18.295299+00'),
	(597, 230, 'Invoice / receipt', 'Outpatient bill', 'bill', 226, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.300307+00', '2026-10-25 15:05:18.30031+00'),
	(598, 231, 'Laboratory report', 'Complete blood count (2026-10-19)', 'lab', 316, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.308229+00', '2026-10-25 15:05:18.309031+00'),
	(599, 231, 'Radiology report', 'Ultrasound Abdomen', 'radiology', 76, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.311496+00', '2026-10-25 15:05:18.311499+00'),
	(600, 231, 'Invoice / receipt', 'Outpatient bill', 'bill', 227, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.317349+00', '2026-10-25 15:05:18.317352+00');
INSERT INTO public.patient_deliverable (id, patient_id, kind, title, ref_type, ref_id, document_id, digital_available, physical_status, physical_note, received_by_name, handed_over_at, handed_over_by_id, created_by_id, created_at, updated_at) VALUES
	(601, 232, 'Laboratory report', 'Complete blood count (2026-10-23)', 'lab', 317, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.325621+00', '2026-10-25 15:05:18.325624+00'),
	(602, 232, 'Invoice / receipt', 'Outpatient bill', 'bill', 228, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.331113+00', '2026-10-25 15:05:18.331115+00'),
	(603, 233, 'Laboratory report', 'Complete blood count (2026-10-22)', 'lab', 318, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.339658+00', '2026-10-25 15:05:18.340425+00'),
	(604, 233, 'Radiology report', 'X-ray Knee, AP/lateral', 'radiology', 77, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.342615+00', '2026-10-25 15:05:18.342617+00'),
	(605, 233, 'Invoice / receipt', 'Outpatient bill', 'bill', 229, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.346856+00', '2026-10-25 15:05:18.346859+00'),
	(606, 234, 'Laboratory report', 'Complete blood count (2026-10-19)', 'lab', 319, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.382844+00', '2026-10-25 15:05:18.384296+00'),
	(607, 234, 'Invoice / receipt', 'Inpatient bill', 'bill', 230, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.390297+00', '2026-10-25 15:05:18.3903+00'),
	(608, 235, 'Laboratory report', 'Renal function (2026-10-24)', 'lab', 320, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.39968+00', '2026-10-25 15:05:18.400592+00'),
	(609, 235, 'Laboratory report', 'Complete blood count (2026-10-24)', 'lab', 321, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.40563+00', '2026-10-25 15:05:18.40719+00'),
	(610, 235, 'Invoice / receipt', 'Outpatient bill', 'bill', 231, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.413778+00', '2026-10-25 15:05:18.413781+00'),
	(611, 236, 'Laboratory report', 'Complete blood count (2026-10-16)', 'lab', 322, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.424131+00', '2026-10-25 15:05:18.425148+00'),
	(612, 236, 'Radiology report', 'X-ray Knee, AP/lateral', 'radiology', 78, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.428408+00', '2026-10-25 15:05:18.428412+00'),
	(613, 236, 'Invoice / receipt', 'Outpatient bill', 'bill', 232, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.435863+00', '2026-10-25 15:05:18.435867+00'),
	(614, 237, 'Laboratory report', 'Lipid profile (2026-10-24)', 'lab', 323, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.449994+00', '2026-10-25 15:05:18.451091+00'),
	(615, 237, 'Laboratory report', 'Complete blood count (2026-10-18)', 'lab', 324, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.456157+00', '2026-10-25 15:05:18.45616+00'),
	(616, 237, 'Radiology report', 'X-ray Chest, PA', 'radiology', 79, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.45962+00', '2026-10-25 15:05:18.459623+00'),
	(617, 237, 'Invoice / receipt', 'Outpatient bill', 'bill', 233, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.466189+00', '2026-10-25 15:05:18.466192+00'),
	(618, 238, 'Discharge summary', 'Discharge summary - Orthopaedic Ward (2026-10-19 to 2026-10-25)', 'admission', 95, NULL, true, 'Ready for collection', '', '', NULL, NULL, 13, '2026-10-25 15:05:18.503606+00', '2026-10-25 15:05:18.506439+00'),
	(619, 238, 'Laboratory report', 'Complete blood count (2026-10-15)', 'lab', 325, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.512512+00', '2026-10-25 15:05:18.513426+00'),
	(620, 238, 'Radiology report', 'X-ray Knee, AP/lateral', 'radiology', 80, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.516452+00', '2026-10-25 15:05:18.516455+00'),
	(621, 238, 'Invoice / receipt', 'Inpatient bill', 'bill', 234, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.523524+00', '2026-10-25 15:05:18.523527+00'),
	(622, 239, 'Laboratory report', 'Lipid profile (2026-10-16)', 'lab', 326, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.532697+00', '2026-10-25 15:05:18.533543+00'),
	(623, 239, 'Laboratory report', 'Complete blood count (2026-10-17)', 'lab', 327, NULL, true, 'Requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.53855+00', '2026-10-25 15:05:18.539708+00'),
	(624, 239, 'Radiology report', 'X-ray Chest, PA', 'radiology', 81, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.542679+00', '2026-10-25 15:05:18.542682+00'),
	(625, 239, 'Invoice / receipt', 'Outpatient bill', 'bill', 235, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.548214+00', '2026-10-25 15:05:18.548217+00'),
	(626, 240, 'Laboratory report', 'Thyroid panel (2026-10-24)', 'lab', 328, NULL, true, 'Not requested', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.558512+00', '2026-10-25 15:05:18.558515+00'),
	(627, 240, 'Invoice / receipt', 'Outpatient bill', 'bill', 236, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.56499+00', '2026-10-25 15:05:18.564993+00'),
	(628, 241, 'Discharge summary', 'Discharge summary - Orthopaedic Ward (2026-10-14 to 2026-10-25)', 'admission', 96, NULL, true, 'Ready for collection', '', '', NULL, NULL, 13, '2026-10-25 15:05:18.600814+00', '2026-10-25 15:05:18.603123+00'),
	(629, 241, 'Laboratory report', 'Complete blood count (2026-10-19)', 'lab', 329, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.608192+00', '2026-10-25 15:05:18.608924+00'),
	(630, 241, 'Radiology report', 'X-ray Knee, AP/lateral', 'radiology', 82, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.61133+00', '2026-10-25 15:05:18.611334+00'),
	(631, 241, 'Invoice / receipt', 'Inpatient bill', 'bill', 237, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.616445+00', '2026-10-25 15:05:18.616448+00'),
	(632, 242, 'Laboratory report', 'Blood glucose (2026-10-20)', 'lab', 330, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.624605+00', '2026-10-25 15:05:18.62546+00'),
	(633, 242, 'Laboratory report', 'Renal function (2026-10-19)', 'lab', 331, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.629521+00', '2026-10-25 15:05:18.630871+00'),
	(634, 242, 'Invoice / receipt', 'Outpatient bill', 'bill', 238, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.635481+00', '2026-10-25 15:05:18.635484+00'),
	(635, 243, 'Laboratory report', 'Lipid profile (2026-10-15)', 'lab', 332, NULL, true, 'Ready for collection', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.642861+00', '2026-10-25 15:05:18.644045+00'),
	(636, 243, 'Invoice / receipt', 'Outpatient bill', 'bill', 239, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.648341+00', '2026-10-25 15:05:18.648344+00'),
	(637, 244, 'Laboratory report', 'Renal function (2026-10-21)', 'lab', 333, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.657956+00', '2026-10-25 15:05:18.658641+00'),
	(638, 244, 'Invoice / receipt', 'Outpatient bill', 'bill', 240, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.665647+00', '2026-10-25 15:05:18.66565+00'),
	(639, 245, 'Invoice / receipt', 'Outpatient bill', 'bill', 241, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.678368+00', '2026-10-25 15:05:18.678371+00'),
	(640, 246, 'Laboratory report', 'Complete blood count (2026-10-17)', 'lab', 336, NULL, true, 'Handed over', '', '', NULL, NULL, 7, '2026-10-25 15:05:18.687682+00', '2026-10-25 15:05:18.688644+00'),
	(641, 246, 'Radiology report', 'Ultrasound Abdomen', 'radiology', 83, NULL, true, 'Not requested', '', '', NULL, NULL, 9, '2026-10-25 15:05:18.692+00', '2026-10-25 15:05:18.692004+00'),
	(642, 246, 'Invoice / receipt', 'Outpatient bill', 'bill', 242, NULL, true, 'Not requested', '', '', NULL, NULL, 10, '2026-10-25 15:05:18.698959+00', '2026-10-25 15:05:18.698962+00');


--
-- Data for Name: payment; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.payment (id, bill_id, kind, amount, method, reference, reason, received_by_id, approved_by_id, created_at) VALUES
	(1, 2, 'Payment', 346.24, 'Card', 'RCPT-00002', '', 10, NULL, '2026-10-25 15:05:09.983207+00'),
	(2, 3, 'Payment', 423.72, 'UPI', 'RCPT-00003', '', 10, NULL, '2026-10-25 15:05:10.048146+00'),
	(3, 4, 'Payment', 182.13, 'Card', 'RCPT-00004', '', 10, NULL, '2026-10-25 15:05:10.074957+00'),
	(4, 5, 'Payment', 323.23, 'Card', 'RCPT-00005', '', 10, NULL, '2026-10-25 15:05:10.127045+00'),
	(5, 6, 'Payment', 238.78, 'UPI', 'RCPT-00006', '', 10, NULL, '2026-10-25 15:05:10.17051+00'),
	(6, 7, 'Payment', 174.21, 'Cash', 'RCPT-00007', '', 10, NULL, '2026-10-25 15:05:10.190823+00'),
	(7, 8, 'Payment', 704.79, 'Cash', 'RCPT-00008', '', 10, NULL, '2026-10-25 15:05:10.241217+00'),
	(8, 9, 'Payment', 175.64, 'Cash', 'RCPT-00009', '', 10, NULL, '2026-10-25 15:05:10.258687+00'),
	(9, 10, 'Payment', 301.29, 'Card', 'RCPT-00010', '', 10, NULL, '2026-10-25 15:05:10.274047+00'),
	(10, 12, 'Payment', 206.83, 'Card', 'RCPT-00012', '', 10, NULL, '2026-10-25 15:05:10.329212+00'),
	(11, 13, 'Payment', 847.34, 'Card', 'RCPT-00013', '', 10, NULL, '2026-10-25 15:05:10.359434+00'),
	(12, 16, 'Payment', 163.02, 'UPI', 'RCPT-00016', '', 10, NULL, '2026-10-25 15:05:10.439637+00'),
	(13, 17, 'Payment', 496.8, 'Cash', 'RCPT-00017', '', 10, NULL, '2026-10-25 15:05:10.479588+00'),
	(14, 18, 'Payment', 936.83, 'UPI', 'RCPT-00018', '', 10, NULL, '2026-10-25 15:05:10.528018+00'),
	(15, 19, 'Payment', 218.4, 'UPI', 'RCPT-00019', '', 10, NULL, '2026-10-25 15:05:10.576248+00'),
	(16, 20, 'Payment', 478.75, 'Cash', 'RCPT-00020', '', 10, NULL, '2026-10-25 15:05:10.609295+00'),
	(17, 21, 'Payment', 613.43, 'UPI', 'RCPT-00021', '', 10, NULL, '2026-10-25 15:05:10.642969+00'),
	(18, 23, 'Payment', 404.46, 'Card', 'RCPT-00023', '', 10, NULL, '2026-10-25 15:05:10.690161+00'),
	(19, 24, 'Payment', 754.72, 'UPI', 'RCPT-00024', '', 10, NULL, '2026-10-25 15:05:10.724336+00'),
	(20, 25, 'Payment', 180.91, 'Cash', 'RCPT-00025', '', 10, NULL, '2026-10-25 15:05:10.738665+00'),
	(21, 26, 'Payment', 691.91, 'UPI', 'RCPT-00026', '', 10, NULL, '2026-10-25 15:05:10.77681+00'),
	(22, 27, 'Payment', 295.61, 'UPI', 'RCPT-00027', '', 10, NULL, '2026-10-25 15:05:10.802432+00'),
	(23, 28, 'Payment', 836.73, 'Card', 'RCPT-00028', '', 10, NULL, '2026-10-25 15:05:10.844319+00'),
	(24, 29, 'Payment', 210.31, 'Cash', 'RCPT-00029', '', 10, NULL, '2026-10-25 15:05:10.860939+00'),
	(25, 30, 'Payment', 414.05, 'UPI', 'RCPT-00030', '', 10, NULL, '2026-10-25 15:05:10.880327+00'),
	(26, 32, 'Payment', 669.43, 'Cash', 'RCPT-00032', '', 10, NULL, '2026-10-25 15:05:10.930636+00'),
	(27, 33, 'Payment', 317.38, 'UPI', 'RCPT-00033', '', 10, NULL, '2026-10-25 15:05:10.969721+00'),
	(28, 34, 'Payment', 198.94, 'Cash', 'RCPT-00034', '', 10, NULL, '2026-10-25 15:05:10.990039+00'),
	(29, 35, 'Payment', 145.79, 'Card', 'RCPT-00035', '', 10, NULL, '2026-10-25 15:05:11.007602+00'),
	(30, 36, 'Payment', 165.37, 'UPI', 'RCPT-00036', '', 10, NULL, '2026-10-25 15:05:11.038175+00'),
	(31, 37, 'Payment', 182.3, 'Card', 'RCPT-00037', '', 10, NULL, '2026-10-25 15:05:11.055973+00'),
	(32, 38, 'Payment', 203.28, 'Cash', 'RCPT-00038', '', 10, NULL, '2026-10-25 15:05:11.076474+00'),
	(33, 40, 'Payment', 293.18, 'Card', 'RCPT-00040', '', 10, NULL, '2026-10-25 15:05:11.150515+00'),
	(34, 41, 'Payment', 398.66, 'Card', 'RCPT-00041', '', 10, NULL, '2026-10-25 15:05:11.165322+00'),
	(35, 42, 'Payment', 312.46, 'Cash', 'RCPT-00042', '', 10, NULL, '2026-10-25 15:05:11.18384+00'),
	(36, 43, 'Payment', 332.44, 'UPI', 'RCPT-00043', '', 10, NULL, '2026-10-25 15:05:12.568771+00'),
	(37, 44, 'Payment', 234.31, 'UPI', 'RCPT-00044', '', 10, NULL, '2026-10-25 15:05:12.599842+00'),
	(38, 45, 'Payment', 347.25, 'Cash', 'RCPT-00045', '', 10, NULL, '2026-10-25 15:05:12.62291+00'),
	(39, 46, 'Payment', 659.55, 'Card', 'RCPT-00046', '', 10, NULL, '2026-10-25 15:05:12.71639+00'),
	(40, 47, 'Payment', 1280.86, 'Cash', 'RCPT-00047', '', 10, NULL, '2026-10-25 15:05:12.756624+00'),
	(41, 48, 'Payment', 957.28, 'Card', 'RCPT-00048', '', 10, NULL, '2026-10-25 15:05:12.802751+00'),
	(42, 49, 'Payment', 1576.1, 'Insurance', 'RCPT-00049', '', 10, NULL, '2026-10-25 15:05:12.864532+00'),
	(43, 50, 'Payment', 128.4, 'Cash', 'RCPT-00050', '', 10, NULL, '2026-10-25 15:05:12.888521+00'),
	(44, 51, 'Payment', 129.3, 'Cash', 'RCPT-00051', '', 10, NULL, '2026-10-25 15:05:12.905906+00'),
	(45, 53, 'Payment', 1889.32, 'Card', 'RCPT-00053', '', 10, NULL, '2026-10-25 15:05:12.962787+00'),
	(46, 54, 'Payment', 376.91, 'Cash', 'RCPT-00054', '', 10, NULL, '2026-10-25 15:05:12.989821+00'),
	(47, 57, 'Payment', 1543.08, 'Insurance', 'RCPT-00057', '', 10, NULL, '2026-10-25 15:05:13.102124+00'),
	(48, 59, 'Payment', 1062.78, 'Cash', 'RCPT-00059', '', 10, NULL, '2026-10-25 15:05:13.204461+00'),
	(49, 60, 'Payment', 509.97, 'Insurance', 'RCPT-00060', '', 10, NULL, '2026-10-25 15:05:13.220914+00'),
	(50, 61, 'Payment', 199.85, 'UPI', 'RCPT-00061', '', 10, NULL, '2026-10-25 15:05:13.237413+00'),
	(51, 62, 'Payment', 1080.99, 'UPI', 'RCPT-00062', '', 10, NULL, '2026-10-25 15:05:13.272406+00'),
	(52, 64, 'Payment', 1505.46, 'Insurance', 'RCPT-00064', '', 10, NULL, '2026-10-25 15:05:13.376923+00'),
	(53, 65, 'Payment', 258.28, 'Card', 'RCPT-00065', '', 10, NULL, '2026-10-25 15:05:13.396102+00'),
	(54, 67, 'Payment', 1444.32, 'UPI', 'RCPT-00067', '', 10, NULL, '2026-10-25 15:05:13.452174+00'),
	(55, 68, 'Payment', 445.58, 'UPI', 'RCPT-00068', '', 10, NULL, '2026-10-25 15:05:13.470126+00'),
	(56, 70, 'Payment', 243.53, 'Card', 'RCPT-00070', '', 10, NULL, '2026-10-25 15:05:13.508604+00'),
	(57, 71, 'Payment', 1455.75, 'UPI', 'RCPT-00071', '', 10, NULL, '2026-10-25 15:05:13.556887+00'),
	(58, 72, 'Payment', 839.36, 'Card', 'RCPT-00072', '', 10, NULL, '2026-10-25 15:05:13.596333+00'),
	(59, 73, 'Payment', 190.7, 'Cash', 'RCPT-00073', '', 10, NULL, '2026-10-25 15:05:13.612196+00'),
	(60, 74, 'Payment', 1308.35, 'Card', 'RCPT-00074', '', 10, NULL, '2026-10-25 15:05:13.642526+00'),
	(61, 75, 'Payment', 398.89, 'Card', 'RCPT-00075', '', 10, NULL, '2026-10-25 15:05:13.662357+00'),
	(62, 76, 'Payment', 2583.47, 'Cash', 'RCPT-00076', '', 10, NULL, '2026-10-25 15:05:13.715295+00'),
	(63, 78, 'Payment', 2039.83, 'UPI', 'RCPT-00078', '', 10, NULL, '2026-10-25 15:05:13.787713+00'),
	(64, 79, 'Payment', 774.93, 'Cash', 'RCPT-00079', '', 10, NULL, '2026-10-25 15:05:13.820392+00'),
	(65, 80, 'Payment', 375.04, 'Cash', 'RCPT-00080', '', 10, NULL, '2026-10-25 15:05:13.831527+00'),
	(66, 81, 'Payment', 584.02, 'Cash', 'RCPT-00081', '', 10, NULL, '2026-10-25 15:05:13.856502+00'),
	(67, 82, 'Payment', 189.62, 'Cash', 'RCPT-00082', '', 10, NULL, '2026-10-25 15:05:13.876287+00'),
	(68, 83, 'Payment', 726.25, 'UPI', 'RCPT-00083', '', 10, NULL, '2026-10-25 15:05:13.91398+00'),
	(69, 84, 'Payment', 205.35, 'UPI', 'RCPT-00084', '', 10, NULL, '2026-10-25 15:05:13.93182+00'),
	(70, 85, 'Payment', 214.13, 'Card', 'RCPT-00085', '', 10, NULL, '2026-10-25 15:05:13.945673+00'),
	(71, 86, 'Payment', 136.12, 'Cash', 'RCPT-00086', '', 10, NULL, '2026-10-25 15:05:13.957499+00'),
	(72, 87, 'Payment', 402.66, 'Card', 'RCPT-00087', '', 10, NULL, '2026-10-25 15:05:13.97218+00'),
	(73, 89, 'Payment', 1275.29, 'Cash', 'RCPT-00089', '', 10, NULL, '2026-10-25 15:05:14.038144+00'),
	(74, 90, 'Payment', 1451.4, 'Cash', 'RCPT-00090', '', 10, NULL, '2026-10-25 15:05:14.106353+00'),
	(75, 91, 'Payment', 1567.07, 'UPI', 'RCPT-00091', '', 10, NULL, '2026-10-25 15:05:14.153594+00'),
	(76, 92, 'Payment', 375.89, 'Insurance', 'RCPT-00092', '', 10, NULL, '2026-10-25 15:05:14.172072+00'),
	(77, 93, 'Payment', 604.93, 'UPI', 'RCPT-00093', '', 10, NULL, '2026-10-25 15:05:14.205065+00'),
	(78, 94, 'Payment', 656.28, 'Insurance', 'RCPT-00094', '', 10, NULL, '2026-10-25 15:05:14.229998+00'),
	(79, 95, 'Payment', 1025.19, 'Card', 'RCPT-00095', '', 10, NULL, '2026-10-25 15:05:14.294913+00'),
	(80, 96, 'Payment', 1030.16, 'UPI', 'RCPT-00096', '', 10, NULL, '2026-10-25 15:05:14.356669+00'),
	(81, 97, 'Payment', 2095.35, 'Card', 'RCPT-00097', '', 10, NULL, '2026-10-25 15:05:14.415954+00'),
	(82, 99, 'Payment', 2178.09, 'Cash', 'RCPT-00099', '', 10, NULL, '2026-10-25 15:05:14.495857+00'),
	(83, 100, 'Payment', 308.33, 'Card', 'RCPT-00100', '', 10, NULL, '2026-10-25 15:05:14.533221+00'),
	(84, 101, 'Payment', 625.56, 'Insurance', 'RCPT-00101', '', 10, NULL, '2026-10-25 15:05:14.57422+00'),
	(85, 102, 'Payment', 334.06, 'UPI', 'RCPT-00102', '', 10, NULL, '2026-10-25 15:05:14.58962+00'),
	(86, 103, 'Payment', 182.09, 'Cash', 'RCPT-00103', '', 10, NULL, '2026-10-25 15:05:14.605335+00'),
	(87, 104, 'Payment', 266.47, 'Card', 'RCPT-00104', '', 10, NULL, '2026-10-25 15:05:14.628924+00'),
	(88, 106, 'Payment', 135.24, 'Card', 'RCPT-00106', '', 10, NULL, '2026-10-25 15:05:14.670788+00'),
	(89, 107, 'Payment', 897.19, 'UPI', 'RCPT-00107', '', 10, NULL, '2026-10-25 15:05:14.73378+00'),
	(90, 108, 'Payment', 1399.76, 'Card', 'RCPT-00108', '', 10, NULL, '2026-10-25 15:05:14.793477+00'),
	(91, 111, 'Payment', 305.92, 'Cash', 'RCPT-00111', '', 10, NULL, '2026-10-25 15:05:14.890488+00'),
	(92, 112, 'Payment', 278.77, 'Insurance', 'RCPT-00112', '', 10, NULL, '2026-10-25 15:05:14.908918+00'),
	(93, 114, 'Payment', 249.55, 'Card', 'RCPT-00114', '', 10, NULL, '2026-10-25 15:05:14.935588+00'),
	(94, 116, 'Payment', 782.8, 'Card', 'RCPT-00116', '', 10, NULL, '2026-10-25 15:05:15.034219+00'),
	(95, 117, 'Payment', 1582.89, 'Insurance', 'RCPT-00117', '', 10, NULL, '2026-10-25 15:05:15.104378+00'),
	(96, 118, 'Payment', 1258.4, 'Card', 'RCPT-00118', '', 10, NULL, '2026-10-25 15:05:15.204762+00'),
	(97, 119, 'Payment', 440.41, 'Card', 'RCPT-00119', '', 10, NULL, '2026-10-25 15:05:15.254829+00'),
	(98, 120, 'Payment', 1842.34, 'UPI', 'RCPT-00120', '', 10, NULL, '2026-10-25 15:05:15.320966+00'),
	(99, 121, 'Payment', 526.52, 'Cash', 'RCPT-00121', '', 10, NULL, '2026-10-25 15:05:15.337775+00'),
	(100, 122, 'Payment', 195.78, 'Cash', 'RCPT-00122', '', 10, NULL, '2026-10-25 15:05:15.367872+00');
INSERT INTO public.payment (id, bill_id, kind, amount, method, reference, reason, received_by_id, approved_by_id, created_at) VALUES
	(101, 123, 'Payment', 829, 'Card', 'RCPT-00123', '', 10, NULL, '2026-10-25 15:05:15.433594+00'),
	(102, 124, 'Payment', 1989.09, 'Card', 'RCPT-00124', '', 10, NULL, '2026-10-25 15:05:15.498134+00'),
	(103, 125, 'Payment', 814.77, 'Card', 'RCPT-00125', '', 10, NULL, '2026-10-25 15:05:15.557521+00'),
	(104, 126, 'Payment', 592.27, 'Insurance', 'RCPT-00126', '', 10, NULL, '2026-10-25 15:05:15.580025+00'),
	(105, 127, 'Payment', 1720.68, 'Insurance', 'RCPT-00127', '', 10, NULL, '2026-10-25 15:05:15.641991+00'),
	(106, 128, 'Payment', 375.97, 'Card', 'RCPT-00128', '', 10, NULL, '2026-10-25 15:05:15.665185+00'),
	(107, 129, 'Payment', 282.81, 'Card', 'RCPT-00129', '', 10, NULL, '2026-10-25 15:05:15.691522+00'),
	(108, 131, 'Payment', 397.35, 'Card', 'RCPT-00131', '', 10, NULL, '2026-10-25 15:05:15.742706+00'),
	(109, 132, 'Payment', 392.05, 'Cash', 'RCPT-00132', '', 10, NULL, '2026-10-25 15:05:15.760891+00'),
	(110, 133, 'Payment', 438.61, 'UPI', 'RCPT-00133', '', 10, NULL, '2026-10-25 15:05:15.780766+00'),
	(111, 134, 'Payment', 140.1, 'UPI', 'RCPT-00134', '', 10, NULL, '2026-10-25 15:05:15.795214+00'),
	(112, 135, 'Payment', 425.06, 'Insurance', 'RCPT-00135', '', 10, NULL, '2026-10-25 15:05:15.807502+00'),
	(113, 136, 'Payment', 1027.99, 'Cash', 'RCPT-00136', '', 10, NULL, '2026-10-25 15:05:15.845399+00'),
	(114, 137, 'Payment', 1712.23, 'Insurance', 'RCPT-00137', '', 10, NULL, '2026-10-25 15:05:15.879527+00'),
	(115, 139, 'Payment', 1009.33, 'Card', 'RCPT-00139', '', 10, NULL, '2026-10-25 15:05:15.951243+00'),
	(116, 141, 'Payment', 219.18, 'UPI', 'RCPT-00141', '', 10, NULL, '2026-10-25 15:05:15.989845+00'),
	(117, 142, 'Payment', 690.51, 'Insurance', 'RCPT-00142', '', 10, NULL, '2026-10-25 15:05:16.024826+00'),
	(118, 143, 'Payment', 277.91, 'Card', 'RCPT-00143', '', 10, NULL, '2026-10-25 15:05:16.043813+00'),
	(119, 144, 'Payment', 839.51, 'UPI', 'RCPT-00144', '', 10, NULL, '2026-10-25 15:05:16.078731+00'),
	(120, 145, 'Payment', 512.14, 'Card', 'RCPT-00145', '', 10, NULL, '2026-10-25 15:05:16.091534+00'),
	(121, 146, 'Payment', 211.43, 'Cash', 'RCPT-00146', '', 10, NULL, '2026-10-25 15:05:16.109295+00'),
	(122, 147, 'Payment', 407.02, 'Cash', 'RCPT-00147', '', 10, NULL, '2026-10-25 15:05:16.149585+00'),
	(123, 149, 'Payment', 453.68, 'Cash', 'RCPT-00149', '', 10, NULL, '2026-10-25 15:05:16.175168+00'),
	(124, 151, 'Payment', 489.34, 'Cash', 'RCPT-00151', '', 10, NULL, '2026-10-25 15:05:16.251813+00'),
	(125, 155, 'Payment', 557.95, 'Cash', 'RCPT-00155', '', 10, NULL, '2026-10-25 15:05:16.324306+00'),
	(126, 156, 'Payment', 212.41, 'Card', 'RCPT-00156', '', 10, NULL, '2026-10-25 15:05:16.338522+00'),
	(127, 158, 'Payment', 182.62, 'UPI', 'RCPT-00158', '', 10, NULL, '2026-10-25 15:05:16.367796+00'),
	(128, 160, 'Payment', 1830.9, 'Cash', 'RCPT-00160', '', 10, NULL, '2026-10-25 15:05:16.428708+00'),
	(129, 161, 'Payment', 512.75, 'Card', 'RCPT-00161', '', 10, NULL, '2026-10-25 15:05:16.442574+00'),
	(130, 162, 'Payment', 209.48, 'UPI', 'RCPT-00162', '', 10, NULL, '2026-10-25 15:05:16.451984+00'),
	(131, 163, 'Payment', 586.36, 'Insurance', 'RCPT-00163', '', 10, NULL, '2026-10-25 15:05:16.470183+00'),
	(132, 164, 'Payment', 335.44, 'UPI', 'RCPT-00164', '', 10, NULL, '2026-10-25 15:05:16.481683+00'),
	(133, 165, 'Payment', 409.97, 'Cash', 'RCPT-00165', '', 10, NULL, '2026-10-25 15:05:16.493833+00'),
	(134, 166, 'Payment', 246.58, 'UPI', 'RCPT-00166', '', 10, NULL, '2026-10-25 15:05:16.503701+00'),
	(135, 167, 'Payment', 115.71, 'Card', 'RCPT-00167', '', 10, NULL, '2026-10-25 15:05:16.515705+00'),
	(136, 168, 'Payment', 432.68, 'Insurance', 'RCPT-00168', '', 10, NULL, '2026-10-25 15:05:16.528399+00'),
	(137, 169, 'Payment', 1211.15, 'UPI', 'RCPT-00169', '', 10, NULL, '2026-10-25 15:05:16.568205+00'),
	(138, 170, 'Payment', 385.85, 'Insurance', 'RCPT-00170', '', 10, NULL, '2026-10-25 15:05:16.577374+00'),
	(139, 171, 'Payment', 454.26, 'Card', 'RCPT-00171', '', 10, NULL, '2026-10-25 15:05:16.586415+00'),
	(140, 172, 'Payment', 446.36, 'Insurance', 'RCPT-00172', '', 10, NULL, '2026-10-25 15:05:16.604182+00'),
	(141, 174, 'Payment', 476.47, 'Card', 'RCPT-00174', '', 10, NULL, '2026-10-25 15:05:16.650752+00'),
	(142, 176, 'Payment', 237.48, 'UPI', 'RCPT-00176', '', 10, NULL, '2026-10-25 15:05:16.675601+00'),
	(143, 177, 'Payment', 1714.4, 'Cash', 'RCPT-00177', '', 10, NULL, '2026-10-25 15:05:16.730922+00'),
	(144, 178, 'Payment', 475.29, 'Cash', 'RCPT-00178', '', 10, NULL, '2026-10-25 15:05:16.744203+00'),
	(145, 179, 'Payment', 508.65, 'Cash', 'RCPT-00179', '', 10, NULL, '2026-10-25 15:05:16.767668+00'),
	(146, 180, 'Payment', 398.07, 'Insurance', 'RCPT-00180', '', 10, NULL, '2026-10-25 15:05:16.793972+00'),
	(147, 181, 'Payment', 137.28, 'Cash', 'RCPT-00181', '', 10, NULL, '2026-10-25 15:05:16.819357+00'),
	(148, 182, 'Payment', 450.07, 'Card', 'RCPT-00182', '', 10, NULL, '2026-10-25 15:05:16.846534+00'),
	(149, 183, 'Payment', 508.48, 'UPI', 'RCPT-00183', '', 10, NULL, '2026-10-25 15:05:16.878228+00'),
	(150, 184, 'Payment', 579.6, 'Insurance', 'RCPT-00184', '', 10, NULL, '2026-10-25 15:05:16.909522+00'),
	(151, 185, 'Payment', 93.97, 'Card', 'RCPT-00185', '', 10, NULL, '2026-10-25 15:05:16.933522+00'),
	(152, 186, 'Payment', 617.33, 'Insurance', 'RCPT-00186', '', 10, NULL, '2026-10-25 15:05:16.963124+00'),
	(153, 187, 'Payment', 1891.05, 'UPI', 'RCPT-00187', '', 10, NULL, '2026-10-25 15:05:17.049727+00'),
	(154, 188, 'Payment', 137.95, 'UPI', 'RCPT-00188', '', 10, NULL, '2026-10-25 15:05:17.107725+00'),
	(155, 189, 'Payment', 145.69, 'Card', 'RCPT-00189', '', 10, NULL, '2026-10-25 15:05:17.130599+00'),
	(156, 190, 'Payment', 1175.42, 'UPI', 'RCPT-00190', '', 10, NULL, '2026-10-25 15:05:17.173927+00'),
	(157, 191, 'Payment', 187.69, 'UPI', 'RCPT-00191', '', 10, NULL, '2026-10-25 15:05:17.193502+00'),
	(158, 193, 'Payment', 4790.1, 'Insurance', 'RCPT-00193', '', 10, NULL, '2026-10-25 15:05:17.308803+00'),
	(159, 194, 'Payment', 306.96, 'Card', 'RCPT-00194', '', 10, NULL, '2026-10-25 15:05:17.329848+00'),
	(160, 195, 'Payment', 1919.12, 'Cash', 'RCPT-00195', '', 10, NULL, '2026-10-25 15:05:17.377045+00'),
	(161, 196, 'Payment', 444.11, 'Cash', 'RCPT-00196', '', 10, NULL, '2026-10-25 15:05:17.392938+00'),
	(162, 197, 'Payment', 382.62, 'Card', 'RCPT-00197', '', 10, NULL, '2026-10-25 15:05:17.406374+00'),
	(163, 198, 'Payment', 3739.79, 'Insurance', 'RCPT-00198', '', 10, NULL, '2026-10-25 15:05:17.459221+00'),
	(164, 200, 'Payment', 564.53, 'Insurance', 'RCPT-00200', '', 10, NULL, '2026-10-25 15:05:17.504645+00'),
	(165, 201, 'Payment', 459.79, 'Cash', 'RCPT-00201', '', 10, NULL, '2026-10-25 15:05:17.525725+00'),
	(166, 202, 'Payment', 530.25, 'Card', 'RCPT-00202', '', 10, NULL, '2026-10-25 15:05:17.546376+00'),
	(167, 203, 'Payment', 1743.84, 'Cash', 'RCPT-00203', '', 10, NULL, '2026-10-25 15:05:17.602791+00'),
	(168, 204, 'Payment', 2202.2, 'UPI', 'RCPT-00204', '', 10, NULL, '2026-10-25 15:05:17.653801+00'),
	(169, 205, 'Payment', 509.96, 'Insurance', 'RCPT-00205', '', 10, NULL, '2026-10-25 15:05:17.676368+00'),
	(170, 206, 'Payment', 421.15, 'Insurance', 'RCPT-00206', '', 10, NULL, '2026-10-25 15:05:17.697463+00'),
	(171, 207, 'Payment', 4601.79, 'Insurance', 'RCPT-00207', '', 10, NULL, '2026-10-25 15:05:17.757723+00'),
	(172, 209, 'Payment', 452.24, 'Insurance', 'RCPT-00209', '', 10, NULL, '2026-10-25 15:05:17.791024+00'),
	(173, 210, 'Payment', 4465.48, 'Insurance', 'RCPT-00210', '', 10, NULL, '2026-10-25 15:05:17.849143+00'),
	(174, 211, 'Payment', 411.97, 'UPI', 'RCPT-00211', '', 10, NULL, '2026-10-25 15:05:17.874874+00'),
	(175, 212, 'Payment', 406.45, 'UPI', 'RCPT-00212', '', 10, NULL, '2026-10-25 15:05:17.903934+00'),
	(176, 213, 'Payment', 1539.66, 'UPI', 'RCPT-00213', '', 10, NULL, '2026-10-25 15:05:17.981848+00'),
	(177, 214, 'Payment', 196.7, 'UPI', 'RCPT-00214', '', 10, NULL, '2026-10-25 15:05:18.000483+00'),
	(178, 215, 'Payment', 221.31, 'Cash', 'RCPT-00215', '', 10, NULL, '2026-10-25 15:05:18.022104+00'),
	(179, 216, 'Payment', 129.82, 'Card', 'RCPT-00216', '', 10, NULL, '2026-10-25 15:05:18.039448+00'),
	(180, 218, 'Payment', 288.3, 'UPI', 'RCPT-00218', '', 10, NULL, '2026-10-25 15:05:18.084617+00'),
	(181, 219, 'Payment', 1469.45, 'Card', 'RCPT-00219', '', 10, NULL, '2026-10-25 15:05:18.152511+00'),
	(182, 220, 'Payment', 205.77, 'UPI', 'RCPT-00220', '', 10, NULL, '2026-10-25 15:05:18.166205+00'),
	(183, 222, 'Payment', 281.98, 'Insurance', 'RCPT-00222', '', 10, NULL, '2026-10-25 15:05:18.223528+00'),
	(184, 223, 'Payment', 232.95, 'UPI', 'RCPT-00223', '', 10, NULL, '2026-10-25 15:05:18.238058+00'),
	(185, 224, 'Payment', 298.19, 'Insurance', 'RCPT-00224', '', 10, NULL, '2026-10-25 15:05:18.251795+00'),
	(186, 225, 'Payment', 368.13, 'Insurance', 'RCPT-00225', '', 10, NULL, '2026-10-25 15:05:18.276195+00'),
	(187, 226, 'Payment', 172.78, 'UPI', 'RCPT-00226', '', 10, NULL, '2026-10-25 15:05:18.29676+00'),
	(188, 227, 'Payment', 521.21, 'Card', 'RCPT-00227', '', 10, NULL, '2026-10-25 15:05:18.313445+00'),
	(189, 228, 'Payment', 457.66, 'Insurance', 'RCPT-00228', '', 10, NULL, '2026-10-25 15:05:18.32759+00'),
	(190, 230, 'Payment', 906.5, 'Card', 'RCPT-00230', '', 10, NULL, '2026-10-25 15:05:18.386091+00'),
	(191, 231, 'Payment', 307.96, 'Card', 'RCPT-00231', '', 10, NULL, '2026-10-25 15:05:18.408458+00'),
	(192, 232, 'Payment', 502.85, 'Card', 'RCPT-00232', '', 10, NULL, '2026-10-25 15:05:18.430953+00'),
	(193, 233, 'Payment', 255.56, 'Cash', 'RCPT-00233', '', 10, NULL, '2026-10-25 15:05:18.462134+00'),
	(194, 234, 'Payment', 1583.15, 'Cash', 'RCPT-00234', '', 10, NULL, '2026-10-25 15:05:18.518985+00'),
	(195, 236, 'Payment', 154.33, 'Card', 'RCPT-00236', '', 10, NULL, '2026-10-25 15:05:18.561126+00'),
	(196, 238, 'Payment', 271.41, 'Cash', 'RCPT-00238', '', 10, NULL, '2026-10-25 15:05:18.631988+00'),
	(197, 239, 'Payment', 124.62, 'UPI', 'RCPT-00239', '', 10, NULL, '2026-10-25 15:05:18.644943+00'),
	(198, 240, 'Payment', 182.34, 'UPI', 'RCPT-00240', '', 10, NULL, '2026-10-25 15:05:18.662241+00'),
	(199, 241, 'Payment', 530.31, 'UPI', 'RCPT-00241', '', 10, NULL, '2026-10-25 15:05:18.674395+00'),
	(200, 242, 'Payment', 521.76, 'Insurance', 'RCPT-00242', '', 10, NULL, '2026-10-25 15:05:18.694573+00');


--
-- Data for Name: prescription; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.prescription (id, patient_id, doctor_name, medicine, dosage, instructions, created_at, ordered_by_id, encounter_id, admission_id, medicine_id, route, frequency, duration_days, quantity, is_prn, status, allergy_override_reason, warnings, verified_by_id, verified_at, cancelled_reason, dispensed_quantity) VALUES
	(1, 1, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:08.05415+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(2, 2, 'Dr. Asha Verma', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:08.054154+00', 3, NULL, NULL, 3, 'Oral', 'Twice daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(3, 6, 'Dr. Asha Verma', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:09.980442+00', 3, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(4, 7, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:10.046893+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(5, 8, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:10.073701+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(6, 9, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:10.126296+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(7, 10, 'Dr. Arjun Nair', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:10.16923+00', 13, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(8, 11, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:10.189539+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(9, 12, 'Dr. Meera Iyer', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:10.239988+00', 12, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(10, 13, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:10.258041+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(11, 14, 'Dr. Asha Verma', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:10.273472+00', 3, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(12, 15, 'Dr. Rohan Das', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:10.308116+00', 15, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(13, 16, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:10.328192+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(14, 17, 'Dr. Meera Iyer', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:10.35884+00', 12, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(15, 18, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:10.376623+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(16, 19, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:10.425707+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(17, 20, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:10.438957+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(18, 21, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:10.478433+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(19, 22, 'Dr. Meera Iyer', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:10.526959+00', 12, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(20, 23, 'Dr. Asha Verma', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:10.575542+00', 3, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(21, 24, 'Dr. Arjun Nair', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:10.608469+00', 13, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(22, 25, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:10.641818+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(23, 26, 'Dr. Asha Verma', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:10.664055+00', 3, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(24, 27, 'Dr. Rohan Das', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:10.689388+00', 15, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(25, 28, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:10.723579+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(26, 29, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:10.737946+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(27, 30, 'Dr. Arjun Nair', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:10.776221+00', 13, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(28, 31, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:10.801681+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(29, 32, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:10.843542+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(30, 33, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:10.860138+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(31, 34, 'Dr. Asha Verma', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:10.87921+00', 3, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(32, 35, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:10.897159+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(33, 36, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:10.929793+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(34, 37, 'Dr. Rohan Das', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:10.969047+00', 15, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(35, 38, 'Dr. Asha Verma', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:10.989327+00', 3, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(36, 39, 'Dr. Asha Verma', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:11.00668+00', 3, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(37, 40, 'Dr. Asha Verma', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:11.037526+00', 3, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(38, 41, 'Dr. Asha Verma', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:11.055238+00', 3, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(39, 42, 'Dr. Asha Verma', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:11.075899+00', 3, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(40, 43, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:11.135893+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(41, 44, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:11.150039+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(42, 45, 'Dr. Asha Verma', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:11.164578+00', 3, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(43, 46, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:11.183238+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(44, 47, 'Dr. Rohan Das', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:12.565812+00', 15, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(45, 48, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:12.598832+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(46, 49, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:12.621699+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(47, 50, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:12.715183+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(48, 51, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:12.755523+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(49, 52, 'Dr. Meera Iyer', 'Atorvastatin 20 mg', '20 mg', '', '2026-10-25 15:05:12.801346+00', 12, NULL, NULL, 7, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(50, 53, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:12.863569+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(51, 54, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:12.887591+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(52, 55, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:12.905073+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(53, 56, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:12.922167+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(54, 57, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:12.961996+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(55, 58, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:12.989078+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(56, 59, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:13.012744+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(57, 60, 'Dr. Fatima Sheikh', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:13.048619+00', 14, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(58, 61, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:13.101244+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(59, 62, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:13.145535+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(60, 63, 'Dr. Rohan Das', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:13.203898+00', 15, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(61, 64, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:13.22032+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(62, 65, 'Dr. Sunita Rao', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:13.236768+00', 16, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(63, 66, 'Dr. Rohan Das', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:13.271802+00', 15, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(64, 67, 'Dr. Meera Iyer', 'Amlodipine 5 mg', '5 mg', '', '2026-10-25 15:05:13.324203+00', 12, NULL, NULL, 11, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(65, 68, 'Dr. Asha Verma', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:13.376018+00', 3, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(66, 69, 'Dr. Meera Iyer', 'Atorvastatin 20 mg', '20 mg', '', '2026-10-25 15:05:13.395377+00', 12, NULL, NULL, 7, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(67, 70, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:13.413466+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(68, 71, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:13.451478+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(69, 72, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:13.468341+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(70, 73, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:13.490519+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(71, 74, 'Dr. Meera Iyer', 'Amlodipine 5 mg', '5 mg', '', '2026-10-25 15:05:13.507948+00', 12, NULL, NULL, 11, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(72, 75, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:13.556115+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(73, 76, 'Dr. Rohan Das', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:13.59568+00', 15, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(74, 77, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:13.611555+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(75, 78, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:13.641714+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(76, 79, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:13.661716+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(77, 80, 'Dr. Rohan Das', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:13.714558+00', 15, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(78, 81, 'Dr. Rohan Das', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:13.732234+00', 15, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(79, 82, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:13.786769+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(80, 83, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:13.819568+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(81, 84, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:13.830789+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(82, 85, 'Dr. Meera Iyer', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:13.855769+00', 12, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(83, 86, 'Dr. Sunita Rao', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:13.875595+00', 16, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(84, 87, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:13.91318+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(85, 88, 'Dr. Rohan Das', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:13.931117+00', 15, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(86, 89, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:13.945122+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(87, 90, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:13.956927+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(88, 91, 'Dr. Asha Verma', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:13.971704+00', 3, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(89, 92, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:13.98808+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(90, 93, 'Dr. Meera Iyer', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:14.037411+00', 12, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(91, 94, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.105346+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(92, 95, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.152647+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(93, 96, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:14.171237+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(94, 97, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.204355+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(95, 98, 'Dr. Meera Iyer', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:14.2289+00', 12, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(96, 99, 'Dr. Fatima Sheikh', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:14.293797+00', 14, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(97, 100, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.355654+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(98, 101, 'Dr. Meera Iyer', 'Amlodipine 5 mg', '5 mg', '', '2026-10-25 15:05:14.41502+00', 12, NULL, NULL, 11, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(99, 102, 'Dr. Meera Iyer', 'Amlodipine 5 mg', '5 mg', '', '2026-10-25 15:05:14.438891+00', 12, NULL, NULL, 11, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(100, 103, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:14.494959+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0);
INSERT INTO public.prescription (id, patient_id, doctor_name, medicine, dosage, instructions, created_at, ordered_by_id, encounter_id, admission_id, medicine_id, route, frequency, duration_days, quantity, is_prn, status, allergy_override_reason, warnings, verified_by_id, verified_at, cancelled_reason, dispensed_quantity) VALUES
	(101, 104, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.532428+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(102, 105, 'Dr. Asha Verma', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:14.57313+00', 3, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(103, 106, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.588947+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(104, 107, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.604499+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(105, 108, 'Dr. Meera Iyer', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:14.627987+00', 12, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(106, 109, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.653914+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(107, 110, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:14.669829+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(108, 111, 'Dr. Asha Verma', 'Salbutamol inhaler', '100 mcg', '', '2026-10-25 15:05:14.732937+00', 3, NULL, NULL, 10, 'Inhaled', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(109, 112, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.792512+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(110, 113, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.817239+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(111, 114, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.83518+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(112, 115, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:14.889499+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(113, 116, 'Dr. Arjun Nair', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.907948+00', 13, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(114, 117, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:14.922886+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(115, 118, 'Dr. Fatima Sheikh', 'Salbutamol inhaler', '100 mcg', '', '2026-10-25 15:05:14.934834+00', 14, NULL, NULL, 10, 'Inhaled', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(116, 119, 'Dr. Meera Iyer', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:14.988344+00', 12, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(117, 120, 'Dr. Meera Iyer', 'Atorvastatin 20 mg', '20 mg', '', '2026-10-25 15:05:15.033247+00', 12, NULL, NULL, 7, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(118, 121, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:15.103122+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(119, 122, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:15.203672+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(120, 123, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:15.253836+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(121, 124, 'Dr. Meera Iyer', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:15.319812+00', 12, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(122, 125, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:15.336922+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(123, 126, 'Dr. Meera Iyer', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:15.366805+00', 12, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(124, 127, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:15.432878+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(125, 128, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:15.497206+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(126, 129, 'Dr. Meera Iyer', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:15.5566+00', 12, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(127, 130, 'Dr. Meera Iyer', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:15.57903+00', 12, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(128, 131, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:15.641031+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(129, 132, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:15.664299+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(130, 133, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:15.690353+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(131, 134, 'Dr. Sunita Rao', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:15.722233+00', 16, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(132, 135, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:15.741704+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(133, 136, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:15.759952+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(134, 137, 'Dr. Arjun Nair', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:15.780182+00', 13, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(135, 138, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:15.794695+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(136, 139, 'Dr. Rohan Das', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:15.806868+00', 15, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(137, 140, 'Dr. Meera Iyer', 'Amlodipine 5 mg', '5 mg', '', '2026-10-25 15:05:15.844632+00', 12, NULL, NULL, 11, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(138, 141, 'Dr. Arjun Nair', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:15.878697+00', 13, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(139, 142, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:15.921039+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(140, 143, 'Dr. Asha Verma', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:15.950691+00', 3, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(141, 144, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:15.981437+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(142, 145, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:15.989284+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(143, 146, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.024125+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(144, 147, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:16.043138+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(145, 148, 'Dr. Asha Verma', 'Salbutamol inhaler', '100 mcg', '', '2026-10-25 15:05:16.078058+00', 3, NULL, NULL, 10, 'Inhaled', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(146, 149, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.090822+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(147, 150, 'Dr. Arjun Nair', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:16.108689+00', 13, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(148, 151, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.148983+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(149, 152, 'Dr. Fatima Sheikh', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:16.157938+00', 14, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(150, 153, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:16.174576+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(151, 154, 'Dr. Fatima Sheikh', 'Salbutamol inhaler', '100 mcg', '', '2026-10-25 15:05:16.217365+00', 14, NULL, NULL, 10, 'Inhaled', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(152, 155, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.251062+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(153, 156, 'Dr. Sunita Rao', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.275648+00', 16, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(154, 157, 'Dr. Asha Verma', 'Salbutamol inhaler', '100 mcg', '', '2026-10-25 15:05:16.292509+00', 3, NULL, NULL, 10, 'Inhaled', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(155, 158, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:16.308502+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(156, 159, 'Dr. Asha Verma', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:16.323649+00', 3, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(157, 160, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.337916+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(158, 161, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:16.354279+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(159, 162, 'Dr. Rohan Das', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:16.367091+00', 15, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(160, 163, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:16.384862+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(161, 164, 'Dr. Rohan Das', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.428092+00', 15, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(162, 165, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:16.442018+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(163, 166, 'Dr. Asha Verma', 'Salbutamol inhaler', '100 mcg', '', '2026-10-25 15:05:16.451192+00', 3, NULL, NULL, 10, 'Inhaled', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(164, 167, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:16.46961+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(165, 168, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.4811+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(166, 169, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:16.493295+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(167, 170, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.503139+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(168, 171, 'Dr. Meera Iyer', 'Atorvastatin 20 mg', '20 mg', '', '2026-10-25 15:05:16.515109+00', 12, NULL, NULL, 7, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(169, 172, 'Dr. Fatima Sheikh', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:16.5277+00', 14, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(170, 173, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:16.567508+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(171, 174, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.576838+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(172, 175, 'Dr. Asha Verma', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:16.585854+00', 3, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(173, 176, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:16.603534+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(174, 177, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:16.638841+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(175, 178, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:16.650168+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(176, 179, 'Dr. Rohan Das', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.663144+00', 15, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(177, 180, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.675003+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(178, 181, 'Dr. Sunita Rao', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.730306+00', 16, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(179, 182, 'Dr. Fatima Sheikh', 'Salbutamol inhaler', '100 mcg', '', '2026-10-25 15:05:16.742653+00', 14, NULL, NULL, 10, 'Inhaled', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(180, 183, 'Dr. Asha Verma', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:16.766389+00', 3, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(181, 184, 'Dr. Asha Verma', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:16.792906+00', 3, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(182, 185, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.818114+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(183, 186, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.845239+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(184, 187, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:16.877036+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(185, 188, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:16.908308+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(186, 189, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:16.932247+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(187, 190, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:16.962019+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(188, 191, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:17.048415+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(189, 192, 'Dr. Arjun Nair', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:17.106977+00', 13, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(190, 193, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:17.129746+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(191, 194, 'Dr. Meera Iyer', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:17.173063+00', 12, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(192, 195, 'Dr. Fatima Sheikh', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:17.19247+00', 14, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(193, 196, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:17.211751+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(194, 197, 'Dr. Meera Iyer', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:17.308099+00', 12, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(195, 198, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:17.328956+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(196, 199, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:17.376558+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(197, 200, 'Dr. Asha Verma', 'Salbutamol inhaler', '100 mcg', '', '2026-10-25 15:05:17.392432+00', 3, NULL, NULL, 10, 'Inhaled', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(198, 201, 'Dr. Rohan Das', 'Pantoprazole 40 mg', '40 mg', '', '2026-10-25 15:05:17.405496+00', 15, NULL, NULL, 8, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(199, 202, 'Dr. Meera Iyer', 'Atorvastatin 20 mg', '20 mg', '', '2026-10-25 15:05:17.45848+00', 12, NULL, NULL, 7, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(200, 203, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:17.48497+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0);
INSERT INTO public.prescription (id, patient_id, doctor_name, medicine, dosage, instructions, created_at, ordered_by_id, encounter_id, admission_id, medicine_id, route, frequency, duration_days, quantity, is_prn, status, allergy_override_reason, warnings, verified_by_id, verified_at, cancelled_reason, dispensed_quantity) VALUES
	(201, 204, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:17.503747+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(202, 205, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:17.524571+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(203, 206, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:17.545403+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(204, 207, 'Dr. Meera Iyer', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:17.601804+00', 12, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(205, 208, 'Dr. Meera Iyer', 'Atorvastatin 20 mg', '20 mg', '', '2026-10-25 15:05:17.652729+00', 12, NULL, NULL, 7, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(206, 209, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:17.675341+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(207, 210, 'Dr. Fatima Sheikh', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:17.696458+00', 14, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(208, 211, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:17.756824+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(209, 212, 'Dr. Fatima Sheikh', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:17.771244+00', 14, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(210, 213, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:17.789962+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(211, 214, 'Dr. Meera Iyer', 'Atorvastatin 20 mg', '20 mg', '', '2026-10-25 15:05:17.848081+00', 12, NULL, NULL, 7, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(212, 215, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:17.873794+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(213, 216, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:17.902851+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(214, 217, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:17.980811+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(215, 218, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:17.999513+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(216, 219, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:18.021039+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(217, 220, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:18.038332+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(218, 221, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:18.052931+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(219, 222, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:18.083513+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(220, 223, 'Dr. Meera Iyer', 'Amlodipine 5 mg', '5 mg', '', '2026-10-25 15:05:18.151768+00', 12, NULL, NULL, 11, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(221, 224, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:18.165573+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(222, 225, 'Dr. Meera Iyer', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:18.211089+00', 12, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(223, 226, 'Dr. Meera Iyer', 'Atorvastatin 20 mg', '20 mg', '', '2026-10-25 15:05:18.222801+00', 12, NULL, NULL, 7, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(224, 227, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:18.237322+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(225, 228, 'Dr. Fatima Sheikh', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:18.250968+00', 14, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(226, 229, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:18.27524+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(227, 230, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:18.295912+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(228, 231, 'Dr. Arjun Nair', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:18.312816+00', 13, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(229, 232, 'Dr. Asha Verma', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:18.326927+00', 3, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(230, 233, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:18.343849+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(231, 234, 'Dr. Fatima Sheikh', 'Salbutamol inhaler', '100 mcg', '', '2026-10-25 15:05:18.384647+00', 14, NULL, NULL, 10, 'Inhaled', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(232, 235, 'Dr. Meera Iyer', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:18.40772+00', 12, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(233, 236, 'Dr. Rohan Das', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:18.43004+00', 15, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(234, 237, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:18.461353+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(235, 238, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:18.518112+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(236, 239, 'Dr. Meera Iyer', 'Aspirin 75 mg', '75 mg', '', '2026-10-25 15:05:18.544361+00', 12, NULL, NULL, 6, 'Oral', 'Once daily', 30, 30, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(237, 240, 'Dr. Asha Verma', 'Levothyroxine 50 mcg', '50 mcg', '', '2026-10-25 15:05:18.560193+00', 3, NULL, NULL, 9, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(238, 241, 'Dr. Arjun Nair', 'Ibuprofen 400 mg', '400 mg', '', '2026-10-25 15:05:18.613127+00', 13, NULL, NULL, 12, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(239, 242, 'Dr. Meera Iyer', 'Metformin 500 mg', '500 mg', '', '2026-10-25 15:05:18.631348+00', 12, NULL, NULL, 3, 'Oral', 'Twice daily', 30, 60, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(240, 243, 'Dr. Meera Iyer', 'Atorvastatin 20 mg', '20 mg', '', '2026-10-25 15:05:18.644371+00', 12, NULL, NULL, 7, 'Oral', 'Twice daily', 10, 20, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(241, 244, 'Dr. Asha Verma', 'Furosemide 40 mg', '40 mg', '', '2026-10-25 15:05:18.661616+00', 3, NULL, NULL, 4, 'Oral', 'Once daily', 14, 14, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(242, 245, 'Dr. Asha Verma', 'Amoxicillin 500 mg', '500 mg', '', '2026-10-25 15:05:18.673744+00', 3, NULL, NULL, 2, 'Oral', 'Three times daily', 7, 21, false, 'Ordered', '', NULL, NULL, NULL, '', 0),
	(243, 246, 'Dr. Arjun Nair', 'Paracetamol 500 mg', '500 mg', '', '2026-10-25 15:05:18.693805+00', 13, NULL, NULL, 1, 'Oral', 'Three times daily', 5, 15, false, 'Ordered', '', NULL, NULL, NULL, '', 0);


--
-- Data for Name: problem; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.problem (id, patient_id, encounter_id, description, code, status, onset_on, recorded_by_id, created_at, resolved_at) VALUES
	(1, 1, NULL, 'Pneumonia, community-acquired', '', 'Active', '2026-09-25', 3, '2026-10-25 15:05:07.832066+00', NULL),
	(2, 2, NULL, 'Type 2 diabetes mellitus', '', 'Active', '2026-09-24', 3, '2026-10-25 15:05:07.837447+00', NULL),
	(3, 3, NULL, 'Post-operative monitoring', '', 'Active', '2026-09-23', 3, '2026-10-25 15:05:07.841432+00', NULL),
	(4, 4, NULL, 'Congestive heart failure', '', 'Active', '2026-09-22', 3, '2026-10-25 15:05:07.844403+00', NULL),
	(5, 6, NULL, 'Migraine with aura', '', 'Active', '2026-06-28', 3, '2026-10-25 15:05:09.887362+00', NULL),
	(6, 7, NULL, 'Hypothyroidism', '', 'Active', '2026-09-04', 3, '2026-10-25 15:05:10.003643+00', NULL),
	(7, 8, NULL, 'Iron-deficiency anaemia', '', 'Active', '2025-11-12', 3, '2026-10-25 15:05:10.060002+00', NULL),
	(8, 9, NULL, 'Type 2 diabetes mellitus', '', 'Active', '2026-02-28', 3, '2026-10-25 15:05:10.086601+00', NULL),
	(9, 10, NULL, 'Acute appendicitis', '', 'Active', '2026-02-20', 13, '2026-10-25 15:05:10.135862+00', NULL),
	(10, 11, NULL, 'Hypertension', '', 'Active', '2026-05-07', 3, '2026-10-25 15:05:10.179829+00', NULL),
	(11, 12, NULL, 'Unstable angina', '', 'Active', '2026-02-15', 12, '2026-10-25 15:05:10.20151+00', NULL),
	(12, 13, NULL, 'Bronchiolitis', '', 'Active', '2026-03-26', 3, '2026-10-25 15:05:10.250861+00', NULL),
	(13, 14, NULL, 'Asthma', '', 'Active', '2026-07-25', 3, '2026-10-25 15:05:10.265324+00', NULL),
	(14, 15, NULL, 'Fractured tibia', '', 'Active', '2026-09-21', 15, '2026-10-25 15:05:10.281159+00', NULL),
	(15, 16, NULL, 'Gestational diabetes', '', 'Active', '2026-10-08', 3, '2026-10-25 15:05:10.316032+00', NULL),
	(16, 17, NULL, 'Coronary artery disease', '', 'Active', '2026-10-06', 12, '2026-10-25 15:05:10.338965+00', NULL),
	(17, 18, NULL, 'Urinary tract infection', '', 'Active', '2026-05-12', 3, '2026-10-25 15:05:10.366761+00', NULL),
	(18, 19, NULL, 'COPD exacerbation', '', 'Active', '2025-10-23', 3, '2026-10-25 15:05:10.388919+00', NULL),
	(19, 20, NULL, 'Osteoarthritis, knee', '', 'Active', '2025-12-31', 3, '2026-10-25 15:05:10.433174+00', NULL),
	(20, 21, NULL, 'Chronic kidney disease', '', 'Active', '2026-05-24', 3, '2026-10-25 15:05:10.446724+00', NULL),
	(21, 22, NULL, 'Heart failure', '', 'Active', '2026-08-17', 12, '2026-10-25 15:05:10.489788+00', NULL),
	(22, 23, NULL, 'Stroke, rehabilitation', '', 'Active', '2025-10-15', 3, '2026-10-25 15:05:10.54006+00', NULL),
	(23, 24, NULL, 'Cholelithiasis', '', 'Active', '2025-11-09', 13, '2026-10-25 15:05:10.583876+00', NULL),
	(24, 25, NULL, 'Dengue fever', '', 'Active', '2026-05-06', 3, '2026-10-25 15:05:10.618758+00', NULL),
	(25, 26, NULL, 'Pre-eclampsia', '', 'Active', '2026-08-26', 3, '2026-10-25 15:05:10.655756+00', NULL),
	(26, 27, NULL, 'Road traffic injury', '', 'Active', '2025-11-25', 15, '2026-10-25 15:05:10.670174+00', NULL),
	(27, 28, NULL, 'Pneumonia', '', 'Active', '2026-01-06', 3, '2026-10-25 15:05:10.698638+00', NULL),
	(28, 29, NULL, 'Type 2 diabetes mellitus', '', 'Active', '2026-08-04', 3, '2026-10-25 15:05:10.731686+00', NULL),
	(29, 30, NULL, 'Hip fracture', '', 'Active', '2026-01-14', 13, '2026-10-25 15:05:10.746336+00', NULL),
	(30, 31, NULL, 'Tonsillitis', '', 'Active', '2026-07-25', 3, '2026-10-25 15:05:10.783241+00', NULL),
	(31, 32, NULL, 'Gastroenteritis', '', 'Active', '2026-08-23', 3, '2026-10-25 15:05:10.812602+00', NULL),
	(32, 33, NULL, 'Hypertension', '', 'Active', '2026-06-01', 3, '2026-10-25 15:05:10.852717+00', NULL),
	(33, 34, NULL, 'Anxiety disorder', '', 'Active', '2026-09-03', 3, '2026-10-25 15:05:10.868874+00', NULL),
	(34, 35, NULL, 'Peptic ulcer disease', '', 'Active', '2026-09-29', 3, '2026-10-25 15:05:10.888753+00', NULL),
	(35, 36, NULL, 'Atrial fibrillation', '', 'Active', '2025-09-23', 12, '2026-10-25 15:05:10.905461+00', NULL),
	(36, 37, NULL, 'Hernia repair', '', 'Active', '2026-04-12', 15, '2026-10-25 15:05:10.940626+00', NULL),
	(37, 38, NULL, 'Thyroid nodule', '', 'Active', '2026-09-23', 3, '2026-10-25 15:05:10.978018+00', NULL),
	(38, 39, NULL, 'Sleep apnoea', '', 'Active', '2026-10-11', 3, '2026-10-25 15:05:10.999235+00', NULL),
	(39, 40, NULL, 'Appendicectomy follow-up', '', 'Active', '2026-01-31', 3, '2026-10-25 15:05:11.018054+00', NULL),
	(40, 41, NULL, 'Lower back pain', '', 'Active', '2026-09-16', 3, '2026-10-25 15:05:11.04393+00', NULL),
	(41, 42, NULL, 'Polycystic ovary syndrome', '', 'Active', '2026-07-26', 3, '2026-10-25 15:05:11.062444+00', NULL),
	(42, 43, NULL, 'Prostate enlargement', '', 'Active', '2026-10-01', 3, '2026-10-25 15:05:11.082933+00', NULL),
	(43, 44, NULL, 'Rheumatoid arthritis', '', 'Active', '2026-01-07', 3, '2026-10-25 15:05:11.142804+00', NULL),
	(44, 45, NULL, 'Cellulitis', '', 'Active', '2025-12-17', 3, '2026-10-25 15:05:11.157+00', NULL),
	(45, 46, NULL, 'Chronic kidney disease', '', 'Active', '2026-01-12', 3, '2026-10-25 15:05:11.173418+00', NULL),
	(46, 47, NULL, 'Lower back pain', '', 'Active', '2025-02-13', 15, '2026-10-25 15:05:12.544563+00', NULL),
	(47, 48, NULL, 'Dengue fever', '', 'Active', '2025-11-08', 3, '2026-10-25 15:05:12.585924+00', NULL),
	(48, 49, NULL, 'Lower back pain', '', 'Active', '2024-09-09', 13, '2026-10-25 15:05:12.612461+00', NULL),
	(49, 50, NULL, 'Hypothyroidism', '', 'Active', '2026-02-24', 3, '2026-10-25 15:05:12.636407+00', NULL),
	(50, 51, NULL, 'Viral fever', '', 'Active', '2025-06-21', 3, '2026-10-25 15:05:12.725331+00', NULL),
	(51, 52, NULL, 'Hyperlipidaemia', '', 'Active', '2026-07-14', 12, '2026-10-25 15:05:12.767834+00', NULL),
	(52, 53, NULL, 'Chronic kidney disease', '', 'Active', '2024-07-31', 3, '2026-10-25 15:05:12.812555+00', NULL),
	(53, 54, NULL, 'Lower back pain', '', 'Active', '2024-12-02', 13, '2026-10-25 15:05:12.874485+00', NULL),
	(54, 55, NULL, 'Viral fever', '', 'Active', '2026-02-21', 3, '2026-10-25 15:05:12.897759+00', NULL),
	(55, 56, NULL, 'Migraine', '', 'Active', '2025-04-14', 3, '2026-10-25 15:05:12.91549+00', NULL),
	(56, 57, NULL, 'Hypothyroidism', '', 'Active', '2026-09-18', 3, '2026-10-25 15:05:12.931522+00', NULL),
	(57, 58, NULL, 'Coronary artery disease', '', 'Active', '2026-04-12', 12, '2026-10-25 15:05:12.971056+00', NULL),
	(58, 59, NULL, 'Urinary tract infection', '', 'Active', '2026-06-18', 3, '2026-10-25 15:05:12.997018+00', NULL),
	(59, 60, NULL, 'Tonsillitis', '', 'Active', '2025-10-05', 14, '2026-10-25 15:05:13.021952+00', NULL),
	(60, 61, NULL, 'Viral fever', '', 'Active', '2025-03-31', 3, '2026-10-25 15:05:13.057027+00', NULL),
	(61, 62, NULL, 'Hypothyroidism', '', 'Active', '2025-12-30', 3, '2026-10-25 15:05:13.112153+00', NULL),
	(62, 63, NULL, 'Lower back pain', '', 'Active', '2026-09-19', 15, '2026-10-25 15:05:13.154343+00', NULL),
	(63, 64, NULL, 'Typhoid fever', '', 'Active', '2026-02-26', 3, '2026-10-25 15:05:13.21035+00', NULL),
	(64, 65, NULL, 'Antenatal check-up, third trimester', '', 'Active', '2026-03-26', 16, '2026-10-25 15:05:13.22697+00', NULL),
	(65, 66, NULL, 'Cholelithiasis', '', 'Active', '2026-10-17', 15, '2026-10-25 15:05:13.244853+00', NULL),
	(66, 67, NULL, 'Essential hypertension', '', 'Active', '2025-10-28', 12, '2026-10-25 15:05:13.279981+00', NULL),
	(67, 68, NULL, 'Peptic ulcer disease', '', 'Active', '2024-06-08', 3, '2026-10-25 15:05:13.331002+00', NULL),
	(68, 69, NULL, 'Hyperlipidaemia', '', 'Active', '2024-11-02', 12, '2026-10-25 15:05:13.388097+00', NULL),
	(69, 70, NULL, 'Migraine', '', 'Active', '2026-08-01', 3, '2026-10-25 15:05:13.40354+00', NULL),
	(70, 71, NULL, 'Coronary artery disease', '', 'Active', '2026-03-28', 12, '2026-10-25 15:05:13.420131+00', NULL),
	(71, 72, NULL, 'Fracture, forearm', '', 'Active', '2024-08-03', 13, '2026-10-25 15:05:13.460509+00', NULL),
	(72, 73, NULL, 'Chronic kidney disease', '', 'Active', '2026-04-13', 3, '2026-10-25 15:05:13.47803+00', NULL),
	(73, 74, NULL, 'Essential hypertension', '', 'Active', '2026-03-13', 12, '2026-10-25 15:05:13.497299+00', NULL),
	(74, 75, NULL, 'Urinary tract infection', '', 'Active', '2026-09-25', 3, '2026-10-25 15:05:13.516476+00', NULL),
	(75, 76, NULL, 'Osteoarthritis, knee', '', 'Active', '2025-08-05', 15, '2026-10-25 15:05:13.563333+00', NULL),
	(76, 77, NULL, 'Fracture, forearm', '', 'Active', '2024-09-10', 13, '2026-10-25 15:05:13.602641+00', NULL),
	(77, 78, NULL, 'Anxiety disorder', '', 'Active', '2026-09-21', 3, '2026-10-25 15:05:13.618916+00', NULL),
	(78, 79, NULL, 'Coronary artery disease', '', 'Active', '2025-04-29', 12, '2026-10-25 15:05:13.650146+00', NULL),
	(79, 80, NULL, 'Cholelithiasis', '', 'Active', '2026-05-09', 15, '2026-10-25 15:05:13.669218+00', NULL),
	(80, 81, NULL, 'Osteoarthritis, knee', '', 'Active', '2024-09-14', 15, '2026-10-25 15:05:13.722336+00', NULL),
	(81, 82, NULL, 'Viral fever', '', 'Active', '2026-05-13', 3, '2026-10-25 15:05:13.740832+00', NULL),
	(82, 83, NULL, 'Dengue fever', '', 'Active', '2026-05-15', 3, '2026-10-25 15:05:13.796754+00', NULL),
	(83, 84, NULL, 'Dengue fever', '', 'Active', '2024-07-15', 3, '2026-10-25 15:05:13.827529+00', NULL),
	(84, 85, NULL, 'Heart failure', '', 'Active', '2025-06-09', 12, '2026-10-25 15:05:13.83935+00', NULL),
	(169, 170, NULL, 'Anxiety disorder', '', 'Active', '2024-07-20', 3, '2026-10-25 15:05:16.500172+00', NULL),
	(85, 86, NULL, 'Antenatal check-up, third trimester', '', 'Active', '2025-05-11', 16, '2026-10-25 15:05:13.86365+00', NULL),
	(86, 87, NULL, 'Anxiety disorder', '', 'Active', '2026-04-26', 3, '2026-10-25 15:05:13.882507+00', NULL),
	(87, 88, NULL, 'Fracture, forearm', '', 'Active', '2026-05-06', 15, '2026-10-25 15:05:13.920908+00', NULL),
	(88, 89, NULL, 'Chronic kidney disease', '', 'Active', '2025-02-16', 3, '2026-10-25 15:05:13.938807+00', NULL),
	(89, 90, NULL, 'Lower back pain', '', 'Active', '2026-07-12', 13, '2026-10-25 15:05:13.951641+00', NULL),
	(90, 91, NULL, 'Peptic ulcer disease', '', 'Active', '2024-08-18', 3, '2026-10-25 15:05:13.964511+00', NULL),
	(91, 92, NULL, 'Coronary artery disease', '', 'Active', '2025-07-13', 12, '2026-10-25 15:05:13.97861+00', NULL),
	(92, 93, NULL, 'Type 2 diabetes mellitus', '', 'Active', '2024-11-30', 12, '2026-10-25 15:05:13.994522+00', NULL),
	(93, 94, NULL, 'Typhoid fever', '', 'Active', '2025-02-11', 3, '2026-10-25 15:05:14.049551+00', NULL),
	(94, 95, NULL, 'Typhoid fever', '', 'Active', '2025-02-21', 3, '2026-10-25 15:05:14.116108+00', NULL),
	(95, 96, NULL, 'Chronic kidney disease', '', 'Active', '2026-05-21', 3, '2026-10-25 15:05:14.161355+00', NULL),
	(96, 97, NULL, 'Viral fever', '', 'Active', '2025-04-13', 3, '2026-10-25 15:05:14.178383+00', NULL),
	(97, 98, NULL, 'Heart failure', '', 'Active', '2025-04-13', 12, '2026-10-25 15:05:14.212084+00', NULL),
	(98, 99, NULL, 'Tonsillitis', '', 'Active', '2024-11-06', 14, '2026-10-25 15:05:14.241176+00', NULL),
	(99, 100, NULL, 'Viral fever', '', 'Active', '2025-07-03', 3, '2026-10-25 15:05:14.306621+00', NULL);
INSERT INTO public.problem (id, patient_id, encounter_id, description, code, status, onset_on, recorded_by_id, created_at, resolved_at) VALUES
	(100, 101, NULL, 'Essential hypertension', '', 'Active', '2026-08-23', 12, '2026-10-25 15:05:14.365507+00', NULL),
	(101, 102, NULL, 'Essential hypertension', '', 'Active', '2025-04-09', 12, '2026-10-25 15:05:14.424821+00', NULL),
	(102, 103, NULL, 'Osteoarthritis, knee', '', 'Active', '2026-04-26', 13, '2026-10-25 15:05:14.447702+00', NULL),
	(103, 104, NULL, 'Iron-deficiency anaemia', '', 'Active', '2024-06-25', 3, '2026-10-25 15:05:14.505054+00', NULL),
	(104, 105, NULL, 'Peptic ulcer disease', '', 'Active', '2025-03-27', 3, '2026-10-25 15:05:14.541363+00', NULL),
	(105, 106, NULL, 'Dengue fever', '', 'Active', '2025-03-19', 3, '2026-10-25 15:05:14.581802+00', NULL),
	(106, 107, NULL, 'Dengue fever', '', 'Active', '2026-02-05', 3, '2026-10-25 15:05:14.59768+00', NULL),
	(107, 108, NULL, 'Type 2 diabetes mellitus', '', 'Active', '2025-08-06', 12, '2026-10-25 15:05:14.613502+00', NULL),
	(108, 109, NULL, 'Typhoid fever', '', 'Active', '2025-09-06', 3, '2026-10-25 15:05:14.636949+00', NULL),
	(109, 110, NULL, 'Urinary tract infection', '', 'Active', '2026-01-18', 3, '2026-10-25 15:05:14.664658+00', NULL),
	(110, 111, NULL, 'Asthma, moderate persistent', '', 'Active', '2026-03-23', 3, '2026-10-25 15:05:14.680788+00', NULL),
	(111, 112, NULL, 'Viral fever', '', 'Active', '2024-05-09', 3, '2026-10-25 15:05:14.743668+00', NULL),
	(112, 113, NULL, 'Migraine', '', 'Active', '2024-07-29', 3, '2026-10-25 15:05:14.804716+00', NULL),
	(113, 114, NULL, 'Anxiety disorder', '', 'Active', '2026-03-28', 3, '2026-10-25 15:05:14.827093+00', NULL),
	(114, 115, NULL, 'Urinary tract infection', '', 'Active', '2026-02-10', 3, '2026-10-25 15:05:14.843964+00', NULL),
	(115, 116, NULL, 'Acute appendicitis', '', 'Active', '2026-08-23', 13, '2026-10-25 15:05:14.89914+00', NULL),
	(116, 117, NULL, 'Dengue fever', '', 'Active', '2025-12-17', 3, '2026-10-25 15:05:14.916466+00', NULL),
	(117, 118, NULL, 'Bronchiolitis', '', 'Active', '2025-11-19', 14, '2026-10-25 15:05:14.93199+00', NULL),
	(118, 119, NULL, 'Heart failure', '', 'Active', '2024-06-04', 12, '2026-10-25 15:05:14.944245+00', NULL),
	(119, 120, NULL, 'Hyperlipidaemia', '', 'Active', '2024-09-06', 12, '2026-10-25 15:05:14.997915+00', NULL),
	(120, 121, NULL, 'Typhoid fever', '', 'Active', '2026-06-08', 3, '2026-10-25 15:05:15.043521+00', NULL),
	(121, 122, NULL, 'Chronic kidney disease', '', 'Active', '2025-12-30', 3, '2026-10-25 15:05:15.116699+00', NULL),
	(122, 123, NULL, 'Typhoid fever', '', 'Active', '2024-09-22', 3, '2026-10-25 15:05:15.215215+00', NULL),
	(123, 124, NULL, 'Heart failure', '', 'Active', '2025-07-04', 12, '2026-10-25 15:05:15.264791+00', NULL),
	(124, 125, NULL, 'Anxiety disorder', '', 'Active', '2024-11-25', 3, '2026-10-25 15:05:15.329441+00', NULL),
	(125, 126, NULL, 'Heart failure', '', 'Active', '2025-06-06', 12, '2026-10-25 15:05:15.349131+00', NULL),
	(126, 127, NULL, 'Hypothyroidism', '', 'Active', '2026-06-16', 3, '2026-10-25 15:05:15.377917+00', NULL),
	(127, 128, NULL, 'Urinary tract infection', '', 'Active', '2026-08-23', 3, '2026-10-25 15:05:15.443695+00', NULL),
	(128, 129, NULL, 'Heart failure', '', 'Active', '2025-02-07', 12, '2026-10-25 15:05:15.50767+00', NULL),
	(129, 130, NULL, 'Heart failure', '', 'Active', '2025-09-11', 12, '2026-10-25 15:05:15.567879+00', NULL),
	(130, 131, NULL, 'Viral fever', '', 'Active', '2025-06-02', 3, '2026-10-25 15:05:15.589547+00', NULL),
	(131, 132, NULL, 'Fracture, forearm', '', 'Active', '2025-05-18', 13, '2026-10-25 15:05:15.65221+00', NULL),
	(132, 133, NULL, 'Community-acquired pneumonia', '', 'Active', '2025-12-12', 3, '2026-10-25 15:05:15.676606+00', NULL),
	(133, 134, NULL, 'Antenatal check-up, third trimester', '', 'Active', '2026-06-25', 16, '2026-10-25 15:05:15.704394+00', NULL),
	(134, 135, NULL, 'Chronic kidney disease', '', 'Active', '2025-05-08', 3, '2026-10-25 15:05:15.732209+00', NULL),
	(135, 136, NULL, 'Hypothyroidism', '', 'Active', '2025-07-18', 3, '2026-10-25 15:05:15.751885+00', NULL),
	(136, 137, NULL, 'Acute appendicitis', '', 'Active', '2025-10-16', 13, '2026-10-25 15:05:15.770656+00', NULL),
	(137, 138, NULL, 'Migraine', '', 'Active', '2026-04-12', 3, '2026-10-25 15:05:15.786922+00', NULL),
	(138, 139, NULL, 'Osteoarthritis, knee', '', 'Active', '2025-04-29', 15, '2026-10-25 15:05:15.8012+00', NULL),
	(139, 140, NULL, 'Essential hypertension', '', 'Active', '2025-03-30', 12, '2026-10-25 15:05:15.814367+00', NULL),
	(140, 141, NULL, 'Cholelithiasis', '', 'Active', '2026-07-06', 13, '2026-10-25 15:05:15.85281+00', NULL),
	(141, 142, NULL, 'Hypothyroidism', '', 'Active', '2024-08-10', 3, '2026-10-25 15:05:15.887593+00', NULL),
	(142, 143, NULL, 'Peptic ulcer disease', '', 'Active', '2025-05-26', 3, '2026-10-25 15:05:15.926934+00', NULL),
	(143, 144, NULL, 'Hypothyroidism', '', 'Active', '2026-02-20', 3, '2026-10-25 15:05:15.957149+00', NULL),
	(144, 145, NULL, 'Migraine', '', 'Active', '2026-06-23', 3, '2026-10-25 15:05:15.987098+00', NULL),
	(145, 146, NULL, 'Typhoid fever', '', 'Active', '2026-07-22', 3, '2026-10-25 15:05:15.996181+00', NULL),
	(146, 147, NULL, 'Urinary tract infection', '', 'Active', '2026-07-12', 3, '2026-10-25 15:05:16.031859+00', NULL),
	(147, 148, NULL, 'Asthma, moderate persistent', '', 'Active', '2025-11-15', 3, '2026-10-25 15:05:16.050724+00', NULL),
	(148, 149, NULL, 'Viral fever', '', 'Active', '2025-01-25', 3, '2026-10-25 15:05:16.085004+00', NULL),
	(149, 150, NULL, 'Cholelithiasis', '', 'Active', '2024-05-26', 13, '2026-10-25 15:05:16.09929+00', NULL),
	(150, 151, NULL, 'Iron-deficiency anaemia', '', 'Active', '2026-06-30', 3, '2026-10-25 15:05:16.117031+00', NULL),
	(151, 152, NULL, 'Tonsillitis', '', 'Active', '2024-10-27', 14, '2026-10-25 15:05:16.155769+00', NULL),
	(152, 153, NULL, 'Urinary tract infection', '', 'Active', '2025-11-21', 3, '2026-10-25 15:05:16.164016+00', NULL),
	(153, 154, NULL, 'Bronchiolitis', '', 'Active', '2026-06-13', 14, '2026-10-25 15:05:16.181418+00', NULL),
	(154, 155, NULL, 'Viral fever', '', 'Active', '2026-03-13', 3, '2026-10-25 15:05:16.224045+00', NULL),
	(155, 156, NULL, 'Antenatal check-up, third trimester', '', 'Active', '2026-04-14', 16, '2026-10-25 15:05:16.260896+00', NULL),
	(156, 157, NULL, 'Asthma, moderate persistent', '', 'Active', '2026-02-21', 3, '2026-10-25 15:05:16.282188+00', NULL),
	(157, 158, NULL, 'Osteoarthritis, knee', '', 'Active', '2025-06-07', 13, '2026-10-25 15:05:16.29966+00', NULL),
	(158, 159, NULL, 'Peptic ulcer disease', '', 'Active', '2026-10-17', 3, '2026-10-25 15:05:16.314971+00', NULL),
	(159, 160, NULL, 'Dengue fever', '', 'Active', '2025-02-08', 3, '2026-10-25 15:05:16.331351+00', NULL),
	(160, 161, NULL, 'Community-acquired pneumonia', '', 'Active', '2025-06-28', 3, '2026-10-25 15:05:16.345784+00', NULL),
	(161, 162, NULL, 'Fracture, forearm', '', 'Active', '2026-01-10', 15, '2026-10-25 15:05:16.361066+00', NULL),
	(162, 163, NULL, 'Coronary artery disease', '', 'Active', '2026-10-08', 12, '2026-10-25 15:05:16.374013+00', NULL),
	(163, 164, NULL, 'Acute appendicitis', '', 'Active', '2025-12-04', 15, '2026-10-25 15:05:16.391107+00', NULL),
	(164, 165, NULL, 'Urinary tract infection', '', 'Active', '2025-09-29', 3, '2026-10-25 15:05:16.434727+00', NULL),
	(165, 166, NULL, 'Asthma, moderate persistent', '', 'Active', '2024-11-22', 3, '2026-10-25 15:05:16.449045+00', NULL),
	(166, 167, NULL, 'Urinary tract infection', '', 'Active', '2025-03-06', 3, '2026-10-25 15:05:16.458283+00', NULL),
	(167, 168, NULL, 'Anxiety disorder', '', 'Active', '2024-09-28', 3, '2026-10-25 15:05:16.476298+00', NULL),
	(168, 169, NULL, 'Urinary tract infection', '', 'Active', '2024-08-30', 3, '2026-10-25 15:05:16.487455+00', NULL),
	(170, 171, NULL, 'Hyperlipidaemia', '', 'Active', '2025-04-30', 12, '2026-10-25 15:05:16.509296+00', NULL),
	(171, 172, NULL, 'Tonsillitis', '', 'Active', '2025-10-21', 14, '2026-10-25 15:05:16.521444+00', NULL),
	(172, 173, NULL, 'Osteoarthritis, knee', '', 'Active', '2024-11-17', 13, '2026-10-25 15:05:16.534961+00', NULL),
	(173, 174, NULL, 'Anxiety disorder', '', 'Active', '2024-10-08', 3, '2026-10-25 15:05:16.574607+00', NULL),
	(174, 175, NULL, 'Peptic ulcer disease', '', 'Active', '2025-07-16', 3, '2026-10-25 15:05:16.583545+00', NULL),
	(175, 176, NULL, 'Chronic kidney disease', '', 'Active', '2024-12-30', 3, '2026-10-25 15:05:16.592928+00', NULL),
	(176, 177, NULL, 'Coronary artery disease', '', 'Active', '2026-01-30', 12, '2026-10-25 15:05:16.610634+00', NULL),
	(177, 178, NULL, 'Hypothyroidism', '', 'Active', '2024-06-25', 3, '2026-10-25 15:05:16.645136+00', NULL),
	(178, 179, NULL, 'Acute appendicitis', '', 'Active', '2026-08-27', 15, '2026-10-25 15:05:16.657364+00', NULL),
	(179, 180, NULL, 'Dengue fever', '', 'Active', '2026-03-27', 3, '2026-10-25 15:05:16.668967+00', NULL),
	(180, 181, NULL, 'Antenatal check-up, third trimester', '', 'Active', '2026-06-04', 16, '2026-10-25 15:05:16.682094+00', NULL),
	(181, 182, NULL, 'Bronchiolitis', '', 'Active', '2026-02-14', 14, '2026-10-25 15:05:16.738971+00', NULL),
	(182, 183, NULL, 'Acute gastroenteritis', '', 'Active', '2025-05-17', 3, '2026-10-25 15:05:16.755659+00', NULL),
	(183, 184, NULL, 'Acute gastroenteritis', '', 'Active', '2025-07-09', 3, '2026-10-25 15:05:16.782859+00', NULL),
	(184, 185, NULL, 'Anxiety disorder', '', 'Active', '2025-09-17', 3, '2026-10-25 15:05:16.80633+00', NULL),
	(185, 186, NULL, 'Iron-deficiency anaemia', '', 'Active', '2025-02-09', 3, '2026-10-25 15:05:16.832191+00', NULL),
	(186, 187, NULL, 'Urinary tract infection', '', 'Active', '2026-07-21', 3, '2026-10-25 15:05:16.859559+00', NULL),
	(187, 188, NULL, 'Typhoid fever', '', 'Active', '2025-02-13', 3, '2026-10-25 15:05:16.890427+00', NULL),
	(188, 189, NULL, 'Hypothyroidism', '', 'Active', '2024-12-15', 3, '2026-10-25 15:05:16.921399+00', NULL),
	(189, 190, NULL, 'Urinary tract infection', '', 'Active', '2026-05-01', 3, '2026-10-25 15:05:16.943736+00', NULL),
	(190, 191, NULL, 'Coronary artery disease', '', 'Active', '2026-01-14', 12, '2026-10-25 15:05:16.973699+00', NULL),
	(191, 192, NULL, 'Acute appendicitis', '', 'Active', '2025-03-13', 13, '2026-10-25 15:05:17.063309+00', NULL),
	(192, 193, NULL, 'Typhoid fever', '', 'Active', '2025-12-21', 3, '2026-10-25 15:05:17.11607+00', NULL),
	(193, 194, NULL, 'Type 2 diabetes mellitus', '', 'Active', '2026-10-21', 12, '2026-10-25 15:05:17.140278+00', NULL),
	(194, 195, NULL, 'Tonsillitis', '', 'Active', '2026-03-28', 14, '2026-10-25 15:05:17.184511+00', NULL),
	(195, 196, NULL, 'Hypothyroidism', '', 'Active', '2026-03-11', 3, '2026-10-25 15:05:17.204562+00', NULL),
	(196, 197, NULL, 'Type 2 diabetes mellitus', '', 'Active', '2024-11-07', 12, '2026-10-25 15:05:17.221207+00', NULL),
	(197, 198, NULL, 'Typhoid fever', '', 'Active', '2024-06-27', 3, '2026-10-25 15:05:17.317162+00', NULL),
	(198, 199, NULL, 'Osteoarthritis, knee', '', 'Active', '2025-11-13', 13, '2026-10-25 15:05:17.338771+00', NULL),
	(199, 200, NULL, 'Asthma, moderate persistent', '', 'Active', '2024-10-17', 3, '2026-10-25 15:05:17.384166+00', NULL),
	(200, 201, NULL, 'Cholelithiasis', '', 'Active', '2024-11-20', 15, '2026-10-25 15:05:17.399102+00', NULL);
INSERT INTO public.problem (id, patient_id, encounter_id, description, code, status, onset_on, recorded_by_id, created_at, resolved_at) VALUES
	(201, 202, NULL, 'Hyperlipidaemia', '', 'Active', '2025-12-16', 12, '2026-10-25 15:05:17.416064+00', NULL),
	(202, 203, NULL, 'Migraine', '', 'Active', '2025-01-08', 3, '2026-10-25 15:05:17.470863+00', NULL),
	(203, 204, NULL, 'Hypothyroidism', '', 'Active', '2025-03-23', 3, '2026-10-25 15:05:17.494421+00', NULL),
	(204, 205, NULL, 'Dengue fever', '', 'Active', '2024-12-04', 3, '2026-10-25 15:05:17.516724+00', NULL),
	(205, 206, NULL, 'Urinary tract infection', '', 'Active', '2026-03-03', 3, '2026-10-25 15:05:17.535923+00', NULL),
	(206, 207, NULL, 'Type 2 diabetes mellitus', '', 'Active', '2024-12-09', 12, '2026-10-25 15:05:17.556888+00', NULL),
	(207, 208, NULL, 'Hyperlipidaemia', '', 'Active', '2026-03-27', 12, '2026-10-25 15:05:17.612534+00', NULL),
	(208, 209, NULL, 'Viral fever', '', 'Active', '2026-05-23', 3, '2026-10-25 15:05:17.665702+00', NULL),
	(209, 210, NULL, 'Tonsillitis', '', 'Active', '2026-03-12', 14, '2026-10-25 15:05:17.687583+00', NULL),
	(210, 211, NULL, 'Coronary artery disease', '', 'Active', '2025-05-04', 12, '2026-10-25 15:05:17.708741+00', NULL),
	(211, 212, NULL, 'Tonsillitis', '', 'Active', '2026-06-25', 14, '2026-10-25 15:05:17.768342+00', NULL),
	(212, 213, NULL, 'Lower back pain', '', 'Active', '2026-01-26', 13, '2026-10-25 15:05:17.780986+00', NULL),
	(213, 214, NULL, 'Hyperlipidaemia', '', 'Active', '2025-08-31', 12, '2026-10-25 15:05:17.7996+00', NULL),
	(214, 215, NULL, 'Urinary tract infection', '', 'Active', '2025-08-09', 3, '2026-10-25 15:05:17.860729+00', NULL),
	(215, 216, NULL, 'Urinary tract infection', '', 'Active', '2025-02-04', 3, '2026-10-25 15:05:17.885657+00', NULL),
	(216, 217, NULL, 'Coronary artery disease', '', 'Active', '2025-12-15', 12, '2026-10-25 15:05:17.91598+00', NULL),
	(217, 218, NULL, 'Migraine', '', 'Active', '2025-06-22', 3, '2026-10-25 15:05:17.992227+00', NULL),
	(218, 219, NULL, 'Migraine', '', 'Active', '2024-11-21', 3, '2026-10-25 15:05:18.008941+00', NULL),
	(219, 220, NULL, 'Hypothyroidism', '', 'Active', '2024-10-09', 3, '2026-10-25 15:05:18.031645+00', NULL),
	(220, 221, NULL, 'Anxiety disorder', '', 'Active', '2026-01-06', 3, '2026-10-25 15:05:18.047114+00', NULL),
	(221, 222, NULL, 'Urinary tract infection', '', 'Active', '2026-09-06', 3, '2026-10-25 15:05:18.067899+00', NULL),
	(222, 223, NULL, 'Essential hypertension', '', 'Active', '2026-07-15', 12, '2026-10-25 15:05:18.096314+00', NULL),
	(223, 224, NULL, 'Anxiety disorder', '', 'Active', '2026-01-11', 3, '2026-10-25 15:05:18.159207+00', NULL),
	(224, 225, NULL, 'Heart failure', '', 'Active', '2025-03-31', 12, '2026-10-25 15:05:18.174752+00', NULL),
	(225, 226, NULL, 'Hyperlipidaemia', '', 'Active', '2024-06-27', 12, '2026-10-25 15:05:18.219898+00', NULL),
	(226, 227, NULL, 'Iron-deficiency anaemia', '', 'Active', '2025-12-08', 3, '2026-10-25 15:05:18.231195+00', NULL),
	(227, 228, NULL, 'Tonsillitis', '', 'Active', '2024-12-28', 14, '2026-10-25 15:05:18.245135+00', NULL),
	(228, 229, NULL, 'Coronary artery disease', '', 'Active', '2024-11-24', 12, '2026-10-25 15:05:18.259843+00', NULL),
	(229, 230, NULL, 'Typhoid fever', '', 'Active', '2026-03-26', 3, '2026-10-25 15:05:18.285992+00', NULL),
	(230, 231, NULL, 'Acute appendicitis', '', 'Active', '2025-05-07', 13, '2026-10-25 15:05:18.303752+00', NULL),
	(231, 232, NULL, 'Dengue fever', '', 'Active', '2026-01-06', 3, '2026-10-25 15:05:18.321471+00', NULL),
	(232, 233, NULL, 'Osteoarthritis, knee', '', 'Active', '2026-09-22', 13, '2026-10-25 15:05:18.335098+00', NULL),
	(233, 234, NULL, 'Bronchiolitis', '', 'Active', '2025-07-01', 14, '2026-10-25 15:05:18.34987+00', NULL),
	(234, 235, NULL, 'Heart failure', '', 'Active', '2025-10-10', 12, '2026-10-25 15:05:18.395357+00', NULL),
	(235, 236, NULL, 'Osteoarthritis, knee', '', 'Active', '2026-06-06', 15, '2026-10-25 15:05:18.418515+00', NULL),
	(236, 237, NULL, 'Coronary artery disease', '', 'Active', '2025-10-07', 12, '2026-10-25 15:05:18.439986+00', NULL),
	(237, 238, NULL, 'Fracture, forearm', '', 'Active', '2026-07-06', 13, '2026-10-25 15:05:18.470212+00', NULL),
	(238, 239, NULL, 'Coronary artery disease', '', 'Active', '2025-03-26', 12, '2026-10-25 15:05:18.527622+00', NULL),
	(239, 240, NULL, 'Hypothyroidism', '', 'Active', '2026-01-09', 3, '2026-10-25 15:05:18.552313+00', NULL),
	(240, 241, NULL, 'Fracture, forearm', '', 'Active', '2026-08-03', 13, '2026-10-25 15:05:18.568868+00', NULL),
	(241, 242, NULL, 'Type 2 diabetes mellitus', '', 'Active', '2025-03-19', 12, '2026-10-25 15:05:18.61999+00', NULL),
	(242, 243, NULL, 'Hyperlipidaemia', '', 'Active', '2026-08-20', 12, '2026-10-25 15:05:18.63879+00', NULL),
	(243, 244, NULL, 'Chronic kidney disease', '', 'Active', '2026-09-07', 3, '2026-10-25 15:05:18.652414+00', NULL),
	(244, 245, NULL, 'Community-acquired pneumonia', '', 'Active', '2025-05-27', 3, '2026-10-25 15:05:18.669471+00', NULL),
	(245, 246, NULL, 'Acute appendicitis', '', 'Active', '2026-06-19', 13, '2026-10-25 15:05:18.682505+00', NULL);


--
-- Data for Name: radiology_record; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.radiology_record (id, patient_id, modality, study_date, findings, report_status, encounter_id, admission_id, ordered_by_id, order_status, study_description, indication, priority, scheduled_at, performed_at, performed_by_id, impression, recommendations, reported_by_id, reported_at, authorized_by_id, authorized_at, urgent_finding, amendment_count, ordered_at) VALUES
	(1, 1, 'X-ray', '2026-10-25', 'Report: patchy opacity in the right lower zone.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Cough and fever', 'Routine', NULL, '2026-10-25 07:05:07.656744+00', 9, 'Appearances may represent consolidation. Clinical correlation advised.', '', 9, '2026-10-25 08:05:07.656744+00', 9, '2026-10-25 08:05:07.656744+00', false, 0, '2026-10-25 15:05:08.046623+00'),
	(2, 6, 'X-ray', '2026-10-23', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Migraine with aura', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:09.96943+00'),
	(3, 8, 'CT', '2026-10-23', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Iron-deficiency anaemia', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.068063+00'),
	(4, 10, 'X-ray', '2026-10-25', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Acute appendicitis', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.163961+00'),
	(5, 12, 'Ultrasound', '2026-10-22', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 12, 'Final', 'Abdomen', 'Unstable angina', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.234467+00'),
	(6, 14, 'MRI', '2026-10-24', 'Mild disc bulge at L4-L5 without cord compression.', 'Final', NULL, NULL, 3, 'Final', 'Lumbar spine', 'Asthma', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Mild degenerative change.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.269824+00'),
	(7, 16, 'X-ray', '2026-10-24', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Gestational diabetes', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.323497+00'),
	(8, 18, 'CT', '2026-10-25', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Urinary tract infection', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.372472+00'),
	(9, 20, 'X-ray', '2026-10-23', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 3, 'Final', 'Knee, AP/lateral', 'Osteoarthritis, knee', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.434844+00'),
	(10, 22, 'Ultrasound', '2026-10-22', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 12, 'Final', 'Abdomen', 'Heart failure', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.521475+00'),
	(11, 24, 'MRI', '2026-10-22', 'Mild disc bulge at L4-L5 without cord compression.', 'Final', NULL, NULL, 13, 'Final', 'Lumbar spine', 'Cholelithiasis', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Mild degenerative change.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.603647+00'),
	(12, 26, 'X-ray', '2026-10-23', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Pre-eclampsia', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.661002+00'),
	(13, 28, 'CT', '2026-10-24', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Pneumonia', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.71963+00'),
	(14, 30, 'X-ray', '2026-10-23', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Hip fracture', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.772832+00'),
	(15, 32, 'Ultrasound', '2026-10-20', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 3, 'Final', 'Abdomen', 'Gastroenteritis', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.839648+00'),
	(16, 34, 'MRI', '2026-10-24', 'Mild disc bulge at L4-L5 without cord compression.', 'Final', NULL, NULL, 3, 'Final', 'Lumbar spine', 'Anxiety disorder', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Mild degenerative change.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.87454+00'),
	(17, 36, 'X-ray', '2026-10-25', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Atrial fibrillation', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.925638+00'),
	(18, 38, 'CT', '2026-10-21', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Thyroid nodule', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:10.98561+00'),
	(19, 40, 'X-ray', '2026-10-24', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 3, 'Final', 'Knee, AP/lateral', 'Appendicectomy follow-up', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:11.033849+00'),
	(20, 42, 'Ultrasound', '2026-10-20', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 3, 'Final', 'Abdomen', 'Polycystic ovary syndrome', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:11.073085+00'),
	(21, 44, 'MRI', '2026-10-23', 'Mild disc bulge at L4-L5 without cord compression.', 'Final', NULL, NULL, 3, 'Final', 'Lumbar spine', 'Rheumatoid arthritis', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'Mild degenerative change.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:11.147505+00'),
	(22, 46, 'X-ray', '2026-10-23', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Chronic kidney disease', 'Routine', NULL, '2026-10-25 05:05:09.687066+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-25 07:05:09.687066+00', 9, '2026-10-25 07:05:09.687066+00', false, 0, '2026-10-25 15:05:11.180651+00'),
	(23, 47, 'MRI', '2026-10-20', 'Mild disc bulge at L4-L5 without cord compression.', 'Final', NULL, NULL, 15, 'Final', 'Lumbar spine', 'Lower back pain', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Mild degenerative change.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:12.552614+00'),
	(24, 54, 'MRI', '2026-10-19', 'Mild disc bulge at L4-L5 without cord compression.', 'Final', NULL, NULL, 13, 'Final', 'Lumbar spine', 'Lower back pain', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Mild degenerative change.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:12.882884+00'),
	(25, 56, 'CT', '2026-10-19', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Migraine', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:12.917539+00'),
	(26, 58, 'X-ray', '2026-10-22', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Coronary artery disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:12.983332+00'),
	(27, 63, 'MRI', '2026-10-17', 'Mild disc bulge at L4-L5 without cord compression.', 'Final', NULL, NULL, 15, 'Final', 'Lumbar spine', 'Lower back pain', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Mild degenerative change.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.200186+00'),
	(28, 65, 'Ultrasound', '2026-10-24', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 16, 'Final', 'Abdomen', 'Antenatal check-up, third trimester', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.23245+00'),
	(29, 66, 'Ultrasound', '2026-10-25', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 15, 'Final', 'Abdomen', 'Cholelithiasis', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.267555+00'),
	(30, 68, 'Ultrasound', '2026-10-24', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 3, 'Final', 'Abdomen', 'Peptic ulcer disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.372552+00'),
	(31, 70, 'CT', '2026-10-25', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Migraine', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.409963+00'),
	(32, 71, 'X-ray', '2026-10-24', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Coronary artery disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.446936+00'),
	(33, 72, 'X-ray', '2026-10-17', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Fracture, forearm', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.46245+00'),
	(34, 77, 'X-ray', '2026-10-24', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Fracture, forearm', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.607831+00'),
	(35, 81, 'X-ray', '2026-10-22', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 15, 'Final', 'Knee, AP/lateral', 'Osteoarthritis, knee', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.727911+00'),
	(36, 85, 'X-ray', '2026-10-21', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Heart failure', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.85215+00'),
	(37, 86, 'Ultrasound', '2026-10-21', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 16, 'Final', 'Abdomen', 'Antenatal check-up, third trimester', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.871729+00'),
	(38, 88, 'X-ray', '2026-10-21', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 15, 'Final', 'Knee, AP/lateral', 'Fracture, forearm', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.92688+00'),
	(39, 91, 'Ultrasound', '2026-10-23', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 3, 'Final', 'Abdomen', 'Peptic ulcer disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.969149+00'),
	(40, 92, 'X-ray', '2026-10-22', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Coronary artery disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:13.984961+00'),
	(41, 98, 'X-ray', '2026-10-23', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Heart failure', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:14.223181+00'),
	(42, 103, 'X-ray', '2026-10-22', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Osteoarthritis, knee', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:14.490637+00'),
	(43, 111, 'X-ray', '2026-10-23', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Asthma, moderate persistent', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:14.728603+00'),
	(44, 113, 'CT', '2026-10-17', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Migraine', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:14.812666+00'),
	(45, 116, 'Ultrasound', '2026-10-17', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 13, 'Final', 'Abdomen', 'Acute appendicitis', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:14.904508+00'),
	(46, 124, 'X-ray', '2026-10-24', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Heart failure', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:15.314851+00'),
	(47, 126, 'X-ray', '2026-10-17', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Heart failure', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:15.362318+00'),
	(48, 129, 'X-ray', '2026-10-25', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Heart failure', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:15.552312+00'),
	(49, 132, 'X-ray', '2026-10-21', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Fracture, forearm', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:15.659747+00'),
	(50, 133, 'X-ray', '2026-10-18', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Community-acquired pneumonia', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:15.685309+00'),
	(51, 134, 'Ultrasound', '2026-10-19', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 16, 'Final', 'Abdomen', 'Antenatal check-up, third trimester', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:15.717882+00'),
	(52, 137, 'Ultrasound', '2026-10-18', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 13, 'Final', 'Abdomen', 'Acute appendicitis', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:15.777366+00'),
	(53, 138, 'CT', '2026-10-17', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Migraine', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:15.791943+00'),
	(54, 143, 'Ultrasound', '2026-10-17', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 3, 'Final', 'Abdomen', 'Peptic ulcer disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:15.947658+00'),
	(55, 148, 'X-ray', '2026-10-17', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Asthma, moderate persistent', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.074683+00'),
	(56, 150, 'Ultrasound', '2026-10-24', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 13, 'Final', 'Abdomen', 'Cholelithiasis', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.105365+00'),
	(57, 154, 'X-ray', '2026-10-21', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 14, 'Final', 'Chest, PA', 'Bronchiolitis', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.213811+00'),
	(58, 156, 'Ultrasound', '2026-10-17', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 16, 'Final', 'Abdomen', 'Antenatal check-up, third trimester', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.272228+00'),
	(59, 157, 'X-ray', '2026-10-25', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Asthma, moderate persistent', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.288005+00'),
	(60, 158, 'X-ray', '2026-10-21', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Osteoarthritis, knee', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.305453+00'),
	(61, 159, 'Ultrasound', '2026-10-22', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 3, 'Final', 'Abdomen', 'Peptic ulcer disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.320548+00'),
	(62, 161, 'X-ray', '2026-10-24', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Community-acquired pneumonia', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.351444+00'),
	(63, 164, 'Ultrasound', '2026-10-24', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 15, 'Final', 'Abdomen', 'Acute appendicitis', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.423468+00'),
	(64, 173, 'X-ray', '2026-10-22', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Osteoarthritis, knee', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.564058+00'),
	(65, 181, 'Ultrasound', '2026-10-18', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 16, 'Final', 'Abdomen', 'Antenatal check-up, third trimester', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:16.726948+00'),
	(66, 191, 'X-ray', '2026-10-20', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Coronary artery disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:17.042444+00'),
	(67, 192, 'Ultrasound', '2026-10-17', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 13, 'Final', 'Abdomen', 'Acute appendicitis', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:17.102343+00'),
	(68, 199, 'X-ray', '2026-10-19', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Osteoarthritis, knee', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:17.373736+00'),
	(69, 200, 'X-ray', '2026-10-24', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 3, 'Final', 'Chest, PA', 'Asthma, moderate persistent', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:17.38916+00'),
	(70, 203, 'CT', '2026-10-24', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Migraine', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:17.48143+00'),
	(71, 211, 'X-ray', '2026-10-21', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Coronary artery disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:17.751853+00'),
	(72, 218, 'CT', '2026-10-22', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Migraine', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:17.994814+00'),
	(73, 219, 'CT', '2026-10-23', 'No intracranial haemorrhage or mass effect.', 'Final', NULL, NULL, 3, 'Final', 'Head, plain', 'Migraine', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute intracranial abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.015179+00'),
	(74, 225, 'X-ray', '2026-10-18', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Heart failure', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.206985+00'),
	(75, 229, 'X-ray', '2026-10-18', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Coronary artery disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.270633+00'),
	(76, 231, 'Ultrasound', '2026-10-24', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 13, 'Final', 'Abdomen', 'Acute appendicitis', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.309459+00'),
	(77, 233, 'X-ray', '2026-10-25', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Osteoarthritis, knee', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.340851+00'),
	(78, 236, 'X-ray', '2026-10-25', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 15, 'Final', 'Knee, AP/lateral', 'Osteoarthritis, knee', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.425804+00'),
	(79, 237, 'X-ray', '2026-10-18', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Coronary artery disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.457102+00'),
	(80, 238, 'X-ray', '2026-10-20', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Fracture, forearm', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.514015+00'),
	(81, 239, 'X-ray', '2026-10-17', 'Lungs are clear. No acute abnormality.', 'Final', NULL, NULL, 12, 'Final', 'Chest, PA', 'Coronary artery disease', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'No acute cardiopulmonary abnormality.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.540364+00'),
	(82, 241, 'X-ray', '2026-10-18', 'Reduced joint space medially with small osteophytes.', 'Final', NULL, NULL, 13, 'Final', 'Knee, AP/lateral', 'Fracture, forearm', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Features of osteoarthritis.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.609303+00'),
	(83, 246, 'Ultrasound', '2026-10-21', 'Normal liver echotexture. No free fluid.', 'Final', NULL, NULL, 13, 'Final', 'Abdomen', 'Acute appendicitis', 'Routine', NULL, '2026-10-24 09:05:12.348598+00', 9, 'Normal abdominal ultrasound.', '', 9, '2026-10-24 13:05:12.348598+00', 9, '2026-10-24 13:05:12.348598+00', false, 0, '2026-10-25 15:05:18.689304+00');


--
-- Data for Name: radiology_report_version; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.radiology_report_version (id, radiology_id, version, findings, impression, recommendations, status, change_reason, author_id, created_at) VALUES
	(1, 1, 1, 'Report: patchy opacity in the right lower zone.', 'Appearances may represent consolidation. Clinical correlation advised.', '', 'Final', '', 9, '2026-10-25 15:05:08.058129+00'),
	(2, 2, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:09.972641+00'),
	(3, 3, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:10.069523+00'),
	(4, 4, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:10.165516+00'),
	(5, 5, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:10.235982+00'),
	(6, 6, 1, 'Mild disc bulge at L4-L5 without cord compression.', 'Mild degenerative change.', '', 'Final', '', 9, '2026-10-25 15:05:10.270947+00'),
	(7, 7, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:10.325102+00'),
	(8, 8, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:10.37367+00'),
	(9, 9, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:10.435624+00'),
	(10, 10, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:10.522781+00'),
	(11, 11, 1, 'Mild disc bulge at L4-L5 without cord compression.', 'Mild degenerative change.', '', 'Final', '', 9, '2026-10-25 15:05:10.604817+00'),
	(12, 12, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:10.661947+00'),
	(13, 13, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:10.720804+00'),
	(14, 14, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:10.773897+00'),
	(15, 15, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:10.840566+00'),
	(16, 16, 1, 'Mild disc bulge at L4-L5 without cord compression.', 'Mild degenerative change.', '', 'Final', '', 9, '2026-10-25 15:05:10.875793+00'),
	(17, 17, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:10.926835+00'),
	(18, 18, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:10.986686+00'),
	(19, 19, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:11.034864+00'),
	(20, 20, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:11.073776+00'),
	(21, 21, 1, 'Mild disc bulge at L4-L5 without cord compression.', 'Mild degenerative change.', '', 'Final', '', 9, '2026-10-25 15:05:11.148302+00'),
	(22, 22, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:11.181357+00'),
	(23, 23, 1, 'Mild disc bulge at L4-L5 without cord compression.', 'Mild degenerative change.', '', 'Final', '', 9, '2026-10-25 15:05:12.555641+00'),
	(24, 24, 1, 'Mild disc bulge at L4-L5 without cord compression.', 'Mild degenerative change.', '', 'Final', '', 9, '2026-10-25 15:05:12.884332+00'),
	(25, 25, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:12.918916+00'),
	(26, 26, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:12.985083+00'),
	(27, 27, 1, 'Mild disc bulge at L4-L5 without cord compression.', 'Mild degenerative change.', '', 'Final', '', 9, '2026-10-25 15:05:13.201548+00'),
	(28, 28, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:13.233433+00'),
	(29, 29, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:13.268309+00'),
	(30, 30, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:13.373444+00'),
	(31, 31, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:13.410757+00'),
	(32, 32, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:13.448513+00'),
	(33, 33, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:13.463198+00'),
	(34, 34, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:13.608617+00'),
	(35, 35, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:13.728784+00'),
	(36, 36, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:13.852865+00'),
	(37, 37, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:13.872716+00'),
	(38, 38, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:13.928066+00'),
	(39, 39, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:13.969798+00'),
	(40, 40, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:13.985714+00'),
	(41, 41, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:14.224745+00'),
	(42, 42, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:14.491775+00'),
	(43, 43, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:14.729624+00'),
	(44, 44, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:14.813854+00'),
	(45, 45, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:14.905338+00'),
	(46, 46, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:15.316812+00'),
	(47, 47, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:15.363487+00'),
	(48, 48, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:15.553221+00'),
	(49, 49, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:15.660899+00'),
	(50, 50, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:15.686616+00'),
	(51, 51, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:15.718958+00'),
	(52, 52, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:15.778107+00'),
	(53, 53, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:15.792683+00'),
	(54, 54, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:15.948446+00'),
	(55, 55, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:16.075566+00'),
	(56, 56, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:16.10618+00'),
	(57, 57, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:16.214675+00'),
	(58, 58, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:16.273099+00'),
	(59, 59, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:16.288823+00'),
	(60, 60, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:16.306181+00'),
	(61, 61, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:16.321355+00'),
	(62, 62, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:16.352183+00'),
	(63, 63, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:16.425567+00'),
	(64, 64, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:16.564855+00'),
	(65, 65, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:16.727765+00'),
	(66, 66, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:17.043936+00'),
	(67, 67, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:17.10384+00'),
	(68, 68, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:17.374513+00'),
	(69, 69, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:17.389885+00'),
	(70, 70, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:17.482232+00'),
	(71, 71, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:17.75299+00'),
	(72, 72, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:17.995908+00'),
	(73, 73, 1, 'No intracranial haemorrhage or mass effect.', 'No acute intracranial abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:18.01742+00'),
	(74, 74, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:18.207973+00'),
	(75, 75, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:18.271789+00'),
	(76, 76, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:18.31019+00'),
	(77, 77, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:18.341538+00'),
	(78, 78, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:18.426865+00'),
	(79, 79, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:18.45812+00'),
	(80, 80, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:18.514952+00'),
	(81, 81, 1, 'Lungs are clear. No acute abnormality.', 'No acute cardiopulmonary abnormality.', '', 'Final', '', 9, '2026-10-25 15:05:18.541347+00'),
	(82, 82, 1, 'Reduced joint space medially with small osteophytes.', 'Features of osteoarthritis.', '', 'Final', '', 9, '2026-10-25 15:05:18.610032+00'),
	(83, 83, 1, 'Normal liver echotexture. No free fluid.', 'Normal abdominal ultrasound.', '', 'Final', '', 9, '2026-10-25 15:05:18.690324+00');


--
-- Data for Name: room; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.room (id, ward_id, label) VALUES
	(1, 1, 'A1'),
	(2, 1, 'A2'),
	(3, 1, 'A3'),
	(4, 2, 'U1'),
	(5, 3, 'W1'),
	(6, 3, 'W2'),
	(7, 3, 'W3'),
	(8, 3, 'W4'),
	(9, 4, 'C1'),
	(10, 4, 'C2'),
	(11, 5, 'S1'),
	(12, 5, 'S2'),
	(13, 5, 'S3'),
	(14, 6, 'WC1'),
	(15, 6, 'WC2'),
	(16, 6, 'WC3'),
	(17, 6, 'WC4'),
	(18, 6, 'WC5'),
	(19, 7, 'WD1'),
	(20, 7, 'WD2'),
	(21, 7, 'WD3'),
	(22, 7, 'WD4'),
	(23, 7, 'WD5'),
	(24, 8, 'MW1'),
	(25, 8, 'MW2'),
	(26, 8, 'MW3'),
	(27, 8, 'MW4'),
	(28, 9, 'PW1'),
	(29, 9, 'PW2'),
	(30, 9, 'PW3'),
	(31, 9, 'PW4'),
	(32, 10, 'OW1'),
	(33, 10, 'OW2'),
	(34, 10, 'OW3'),
	(35, 10, 'OW4'),
	(36, 11, 'HDU1'),
	(37, 11, 'HDU2'),
	(38, 11, 'HDU3');


--
-- Data for Name: stock_movement; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: system_setting; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: ward; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.ward (id, name, department_id, specialty, floor, daily_rate, is_active) VALUES
	(1, 'Ward A', 1, 'General medicine', '', 120, true),
	(2, 'ICU', 3, 'Intensive care', '', 480, true),
	(3, 'Ward B', 1, 'General medicine', '', 140, true),
	(4, 'Cardiac Care', 6, 'Cardiology', '', 300, true),
	(5, 'Surgical Ward', 2, 'Surgery', '', 180, true),
	(6, 'Ward C', 1, 'General medicine', '', 130, true),
	(7, 'Ward D', 1, 'General medicine', '', 130, true),
	(8, 'Maternity Ward', 5, 'Obstetrics', '', 220, true),
	(9, 'Paediatric Ward', 4, 'Paediatrics', '', 160, true),
	(10, 'Orthopaedic Ward', 2, 'Orthopaedics', '', 190, true),
	(11, 'High Dependency Unit', 3, 'High dependency', '', 380, true);


--
-- Name: admission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.admission_id_seq', 96, true);


--
-- Name: ai_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ai_message_id_seq', 1, false);


--
-- Name: alert_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.alert_id_seq', 1, true);


--
-- Name: alert_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.alert_rule_id_seq', 4, true);


--
-- Name: allergy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.allergy_id_seq', 58, true);


--
-- Name: app_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.app_user_id_seq', 76, true);


--
-- Name: appointment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.appointment_id_seq', 347, true);


--
-- Name: audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.audit_log_id_seq', 228, true);


--
-- Name: bed_assignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bed_assignment_id_seq', 96, true);


--
-- Name: bed_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bed_id_seq', 76, true);


--
-- Name: bill_adjustment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bill_adjustment_id_seq', 1, false);


--
-- Name: bill_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bill_id_seq', 242, true);


--
-- Name: care_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.care_plan_id_seq', 1, false);


--
-- Name: care_task_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.care_task_id_seq', 4, true);


--
-- Name: clinical_note_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.clinical_note_id_seq', 96, true);


--
-- Name: critical_ack_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.critical_ack_id_seq', 1, true);


--
-- Name: department_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.department_id_seq', 6, true);


--
-- Name: dispense_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dispense_event_id_seq', 1, false);


--
-- Name: doctor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.doctor_id_seq', 12, true);


--
-- Name: document_page_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.document_page_id_seq', 1, false);


--
-- Name: encounter_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.encounter_id_seq', 96, true);


--
-- Name: follow_up_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.follow_up_id_seq', 1, false);


--
-- Name: handover_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.handover_id_seq', 1, false);


--
-- Name: insurance_claim_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.insurance_claim_id_seq', 1, false);


--
-- Name: intake_output_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.intake_output_id_seq', 1, false);


--
-- Name: lab_report_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.lab_report_id_seq', 336, true);


--
-- Name: lab_result_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.lab_result_id_seq', 707, true);


--
-- Name: med_reconciliation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.med_reconciliation_id_seq', 1, false);


--
-- Name: medical_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.medical_document_id_seq', 1, false);


--
-- Name: medication_administration_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.medication_administration_id_seq', 1, false);


--
-- Name: medicine_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.medicine_id_seq', 12, true);


--
-- Name: monitoring_device_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.monitoring_device_id_seq', 1, false);


--
-- Name: notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notification_id_seq', 4, true);


--
-- Name: observation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.observation_id_seq', 438, true);


--
-- Name: patient_assignment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.patient_assignment_id_seq', 272, true);


--
-- Name: patient_deliverable_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.patient_deliverable_id_seq', 642, true);


--
-- Name: patient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.patient_id_seq', 246, true);


--
-- Name: payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payment_id_seq', 200, true);


--
-- Name: prescription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.prescription_id_seq', 243, true);


--
-- Name: problem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.problem_id_seq', 245, true);


--
-- Name: radiology_record_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.radiology_record_id_seq', 83, true);


--
-- Name: radiology_report_version_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.radiology_report_version_id_seq', 83, true);


--
-- Name: room_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.room_id_seq', 38, true);


--
-- Name: stock_movement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stock_movement_id_seq', 1, false);


--
-- Name: ward_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ward_id_seq', 11, true);
