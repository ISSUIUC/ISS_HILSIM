/*
Alright this is what I'm thinking:
Run table
run id, github user id of the person running, run, file path of the run output data, time of the run was submitted, run start time, runtime, and run end,run status
run status enum:
queued, running, cancelled, success, failed: crashed, failed: compile error, failed: timeout, failed: unknown
Run config
config id, other config stuff
*/
CREATE TABLE "hilsim_runs" (
  "run_id" serial NOT NULL,
  PRIMARY KEY ("run_id"),
  "user_id" varchar(40) NOT NULL,
  "branch" varchar(128) NOT NULL,
  "git_hash" varchar(40) NOT NULL,
  "output_path" varchar(128) NOT NULL,
  "submitted_time" timestamp NOT NULL,
  "run_start" timestamp NULL,
  "run_end" timestamp NULL,
  "run_status" smallint NOT NULL,
  "description" varchar(512) NULL,
  "data_uri" varchar(128) NULL
);
CREATE TABLE "public"."job_configuration" (
    "job_name" character varying(40) NOT NULL,
    "job_type" character varying(10) NOT NULL,
    "json_config" text NOT NULL,
    "time_to_run" timestamp NOT NULL
) WITH (oids = false);

