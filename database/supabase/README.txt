Load CareFlow into Supabase without opening port 5432 (browser only)

Supabase Dashboard > SQL Editor > New query. For each file below, in this exact order:
open it in a text editor, select all, copy, paste into the SQL Editor, press Run, wait for "Success".

  1. 1_schema.sql                     creates the 48 tables
  2. 2_data_part1.sql ... part4.sql   fills them (run part1, then part2, part3, part4)
  3. 9_indexes_and_constraints.sql    adds keys, indexes and rules

If a run fails, send me the error text. Do not run a file twice; if you need to start over, run:
  drop schema public cascade; create schema public;
then load again from file 1.

After loading, Table Editor shows patient (246 rows), app_user (76 rows) and so on.
The app itself still needs port 5432 to run against Supabase (use a phone hotspot), otherwise run it locally with SQLite.
Logins: see careflow_logins.csv (password CareFlow-Demo-2026!).
