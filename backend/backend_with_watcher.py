from datetime import datetime
import mysql.connector
import os
import random
import re
import time
import sys
import zipfile

JOBS_DIR = "/app/jobs"  # used by runAlphafold.sh

TASK_STATE_IN_PROGRESS = 1
TASK_STATE_DONE = 2
TASK_STATE_INVALID = 3

MODEL_PRESET_ARGUMENTS = ['monomer', 'monomer_casp14', 'monomer_ptm', 'multimer']
FULL_DBS_ARGUMENTS = ['reduced_dbs', 'full_dbs']
MODELS_TO_RELAX_ARGUMENT_DICT = {0: "none", 1: "all", 2: "best"}

def db_up():
    global my_db
    try:
        my_db = mysql.connector.connect(
            host =      os.getenv("DB_HOST"),
            user =      os.getenv("DB_USER"),
            password =  os.getenv("DB_PASSWORD"),
            database =  os.getenv("DB_DATABASE"),
            port =      os.getenv("DB_PORT")
        )
        print("Connection to DB successful!")
    except mysql.connector.Error as err:
        print(f"Error connecting to DB: {err}")
        sys.exit(1)

def db_down():
    global my_db
    my_db.close()
    my_db = None

def trace(text):
    print("[TRACE]", text, flush=True)

def add_process_row(task_id, user_id):
    trace(f"add task #{task_id} for user {user_id}")
    task_id = int(task_id)
    user_id = int(user_id)
    mycursor = my_db.cursor()

    sql = "INSERT INTO af_results (id, state, results_file, log_file) VALUES (%s, %s, %s, %s)"
    val = (task_id, 0, f"{user_id}/{task_id}.zip", f"{user_id}/{task_id}.log")
    mycursor.execute(sql, val)

    my_db.commit()

def initialize_new_tasks():
    trace("Initializing new tasks...")
    try:
        mycursor = my_db.cursor()
        mycursor.execute("SELECT id, userId FROM af_tasks WHERE id NOT IN (SELECT id FROM af_results)")
        myresult = mycursor.fetchall()
        trace(f"Found {len(myresult)} new tasks to add.")
        
        for (taskId, userId) in myresult:
            trace(f"Adding task #{taskId} for user {userId}")
            add_process_row(taskId, userId)

        if len(myresult):
            trace("Finished initializing new tasks.")
    except mysql.connector.Error as err:
        trace(f"Database error in initNewTasks: {err}")
    except Exception as e:
        trace(f"Unexpected error in initNewTasks: {e}")

def get_next_task():
    mycursor = my_db.cursor()
    mycursor.execute("""
                SELECT 
                    r.id, 
                    r.results_file, 
                    r.log_file, 
                    t.userId,
                    t.name,
                    t.usercomment,
                    t.fasta,
                    t.model_preset,
                    t.full_dbs,
                    t.models_to_relax,
                    t.enable_gpu_relax,
                    t.max_template_date
                FROM   
                    af_results r 
                left join 
                    af_tasks t on (t.id = r.id) 
                where 
                    r.state = 0 and t.enabled = 1
    """)
    myresult = mycursor.fetchall()
    for x in myresult:
        return list(x)

    return None

def update_task_state(task_id, state):
    trace(f"set task #{task_id} to state {state}")
    mycursor = my_db.cursor()
    sql = "UPDATE af_results set state=%s where id=%s"
    val = (int(state), int(task_id))
    mycursor.execute(sql, val)
    my_db.commit()


def make_user_id(user_id):
    dir = "/app"
    trace("Test dir: " + dir)

    if not os.path.isdir(dir):
        trace("create dir: " + dir)
        os.mkdir(dir)

    dir += "/results"
    trace("Test dir: " + dir)
    if not os.path.isdir(dir):
        trace("create dir: " + dir)
        os.mkdir(dir)

    dir += f"/{user_id}"
    trace("Test dir: " + dir)
    if not os.path.isdir(dir):
        trace("create dir: " + dir)
        os.mkdir(dir)

def is_valid_fasta_sequence(fasta_sequence):
    valid_aminos = "ACDEFGHIKLMNPQRSTVWYBXZ"
    for char in fasta_sequence:
        if char not in valid_aminos:
            return False
    return True

def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_job_currently_running():
    for filename in os.listdir(JOBS_DIR):
        if filename.endswith(".working"):
            return True
    return False

def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_to_file(string, file_path, timestamp=False, include_trace=False):
    if timestamp:
        string = f"[{get_current_timestamp()}] " + string

    with open(file_path, "at") as f:
        print(string, file=f)

    if include_trace:
        trace(string)

def validate_param(val, allowed, name, log_file, task_id):
    if val not in allowed:
        write_to_file(f"[ERROR] {name} '{val}' invalid", log_file, timestamp=True, include_trace=True)
        update_task_state(task_id, TASK_STATE_INVALID)
        raise ValueError(f"{name} invalid")
    
def mark_for_deletion(path, description):
    try:
        if os.path.exists(path):
            new_path = path + ".deleteme"
            os.rename(path, new_path)
            trace(f"Marked {description} for deletion: {new_path}")
    except Exception as e:
        trace(f"Could not mark {description} for deletion: {e}")

# MAIN LOOP
while True:
    db_up()
    print("running DBb")
    initialize_new_tasks()

    # do not get next task if job is already running
    task = None
    if not is_job_currently_running():
        task = get_next_task()

    # outstanding task detected
    if task is not None:
        (task_id, zip_path, log_path, user_id, name, user_comment, fasta, model_preset, full_dbs, models_to_relax, enable_gpu_relax, max_template_date) = task
        task_id = int(task_id)
        user_id = int(user_id)
        output_dir = f"/app/results/{user_id}/{task_id}"
        fasta_log_file = f"{output_dir}.log"
        zip_file = f"{output_dir}.zip"
        fasta_file = f"{JOBS_DIR}/{user_id}-{task_id}.fasta"  # user_id and task_id will be used later to move zipped results to correct folder
        args_file = f"{fasta_file}.args"

        make_user_id(user_id)
        
        trace("Creating log....")
        write_to_file(f"Started task #{task_id}", fasta_log_file, timestamp=True)

        if not is_valid_fasta_sequence(fasta):
            write_to_file(f"[ERROR] Fasta sequence \"{fasta}\" invalid, aborting.", fasta_log_file, timestamp=True, include_trace=True)
            update_task_state(task_id, TASK_STATE_INVALID)
            continue

        # fill default parameters if empty
        model_preset = model_preset or MODEL_PRESET_ARGUMENTS[0]
        full_dbs = full_dbs or 1
        models_to_relax = models_to_relax or 2
        enable_gpu_relax = enable_gpu_relax or 1

        # validate parameters
        try:
            validate_param(model_preset, MODEL_PRESET_ARGUMENTS, "Model preset", fasta_log_file, task_id)
            validate_param(full_dbs, (0,1), "Full DBS", fasta_log_file, task_id)
            validate_param(models_to_relax, (0,1,2), "Models to relax", fasta_log_file, task_id)
            validate_param(enable_gpu_relax, (0,1), "Enable GPU relax", fasta_log_file, task_id)
            if max_template_date and not is_valid_date(max_template_date):
                raise ValueError(f"Max template date '{max_template_date}' invalid")
        except ValueError: 
            continue

        trace("Creating fasta...")
        write_to_file(f">{name}\n{fasta}", fasta_file)

        trace("Creating args file...")
        args_content = " ".join([
            model_preset,
            FULL_DBS_ARGUMENTS[full_dbs],
            MODELS_TO_RELAX_ARGUMENT_DICT[models_to_relax],
            str(bool(enable_gpu_relax)),
            max_template_date or ""
        ])
        write_to_file(args_content, args_file)

        update_task_state(task_id, TASK_STATE_IN_PROGRESS)

    # results from completed job detected
    for filename in os.listdir(JOBS_DIR):
        if not filename.endswith(".fasta.done"):
            continue

        done_path = os.path.join(JOBS_DIR, filename)

        # get user_id and task_id from finished filename
        match = re.match(r"(\d+)-(\d+)\.fasta\.done", filename)
        if not match:
            continue

        user_id = int(match.group(1))
        task_id = int(match.group(2))

        trace(f"Detected completed job: user={user_id}, task={task_id}")

        # zip files
        base_name = f"{user_id}-{task_id}.fasta"
        results_dir = os.path.join(JOBS_DIR, f"{base_name}.results")
        fasta_log_file = os.path.join(JOBS_DIR, f"{base_name}.log")
        args_file = os.path.join(JOBS_DIR, f"{base_name}.args")
        output_dir = f"/app/results/{user_id}"
        zip_path = os.path.join(output_dir, f"{task_id}.zip")

        os.makedirs(output_dir, exist_ok=True)
        
        trace(f"Zipping contents for job: user={user_id}, task={task_id}")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            if (os.path.isdir(results_dir)):
                for root, dirs, files in os.walk(results_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, results_dir)
                        zipf.write(full_path, arcname)

            if os.path.exists(fasta_log_file):
                zipf.write(fasta_log_file, os.path.basename(fasta_log_file))
            
        update_task_state(task_id, TASK_STATE_DONE)
        info_log_file = f"/app/results/{user_id}/{task_id}.log"
        write_to_file(f"Finished task #{task_id}", info_log_file, timestamp=True, include_trace=True)

        mark_for_deletion(done_path, "done file")
        mark_for_deletion(fasta_log_file, "log file")
        mark_for_deletion(args_file, "args file")
        mark_for_deletion(results_dir, "results directory")

    db_down()
    time.sleep(10)
