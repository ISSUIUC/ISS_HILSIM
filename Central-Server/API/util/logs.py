# A utility to log different data to files in the kamaji server
import sys
import os
import datetime

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

import internal.database as database

def write_to_job_log_timestamp(job_id: int, text: str) -> bool:
    """Appends `text` to the output file of `job_id`, also includes timestamp."""
    current_time = datetime.datetime.now()
    write_to_job_log(job_id, f"({current_time}) {text}")

def write_to_job_log(job_id: int, text_to_append: str) -> bool:
    """Appends `text_to_append` to the output file of job `job_id`. Returns whether the operation was successful."""
    conn = database.connect()
    cursor = conn.cursor()

    # Create directory
    cursor.execute("SELECT * FROM hilsim_runs WHERE run_id = %s", (job_id,))
    results = cursor.fetchall()
    if(len(results) != 0):
        output_dir = database.convert_database_tuple(cursor, results[0]).output_path
        if (not os.path.exists(output_dir)):
            os.makedirs(output_dir)
        out_file = os.path.join(output_dir, "kamaji_log.txt")
        fuke = open(out_file, 'a')
        fuke.write(text_to_append + "\n")
        fuke.flush()
        fuke.close()
    return False