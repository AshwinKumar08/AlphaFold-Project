import os
import sys
from flask import request, send_from_directory
import app.user as user
import app.constants as app_constants

mycursor = None
mydb = None
try:
  from app.dbUtil import getDbInstance
  mydb = getDbInstance()
  mycursor = mydb.cursor()
except:
  print("Error occured while connecting to the DB")

'''
fakeTask1 = { "id": 1
            , "enabled": 0
            , "fasta": ">hsa-let-7a-2-3p MIMAT0010195 Homo sapiens let-7a-2-3p\nCUGUACAGCCUCCUAGCUUUCC"
            , "userId": 1
            , "name": "First example task"
            , "userComment": ""
            , "model_preset": "monomer"
            , "full_dbs": 1
            , "models_to_relax": 2
            , "enable_gpu_relax": 1
            , "max_template_date": "2025-05-01"
            , "result": { "state": 0 }
            }

fakeTask2 = { "id": 2
            , "enabled": 1
            , "fasta": ">hsa-let-7a-2-3p MIMAT0010195 Homo sapiens let-7a-2-3p\nCUGUACAGCCUCCUAGCUUUCC"
            , "userId": 1
            , "name": "Second example task"
            , "userComment": ""
            , "model_preset": ""
            , "full_dbs": 1
            , "models_to_relax": 2
            , "enable_gpu_relax": 1
            , "max_template_date": "2025-05-01"
            , "result": { "state": 2, "results_file": "1/2.zip", "log_file": "1/2.log" }
            }

fakeTasks = [ fakeTask1, fakeTask2 ]
'''

def trace(text):
    print(text, file=sys.stderr)

def getTask(taskId, logged_in_user):
  if taskId is None or not str(taskId).isdigit():
    return None

  taskId_int = int(taskId)
  
  if taskId_int is None or f"{taskId_int}" != f"{taskId}":
    return None

  task = []
  try:
    if logged_in_user["is_admin"]:
      mycursor.execute(app_constants.SQL_SELECT_TASK_BY_ID, [taskId_int])
    else:
      mycursor.execute(app_constants.SQL_SELECT_TASK_BY_ID + " AND userId = %s", [taskId_int, logged_in_user["id"]])
    task = mycursor.fetchall()
    trace(f"fetched successfully for task: {taskId_int}")
  except:
    trace(f"Error while fetching task from database for task: {taskId_int}")
    task = []

  if task and len(task) > 0 and task[0]:
    return dict(zip(app_constants.AF_TASKS_KEYS, task[0]))
  else:
    return None

def createEntrypoints(webapp):
  @webapp.get("/api/1.0/<sessionUUID>/task")
  def entrypoint_list_tasks(sessionUUID):
    logged_in_user = user.isLoggedIn(sessionUUID)
    if not logged_in_user:
      return app_constants.PLEASE_LOGIN

    tasks = []
    # print(user.newSession("1","testuser"))
    
    # mycursor.execute("insert INTO af_users (name, user_password, is_admin) values ('test_admin', '$2b$12$.IaNt46x6klPO0FiyDtc8.9hofKaL2BIp4FmBKaOxbkITpO6Y2yXq',1);")
    # mydb.commit()
    # print(mycursor.fetchall())


    try:
      if logged_in_user["is_admin"]:
        mycursor.execute(app_constants.SQL_SELECT_TASKS)
      else:
        mycursor.execute(app_constants.SQL_SELECT_TASKS + " WHERE userId = %s", [logged_in_user["id"]])
      tasks = mycursor.fetchall()
    except:
      trace("Error while fetching tasks from database")
      tasks = []
  
    if tasks and len(tasks) > 0:
      return {"status": "ok", "tasks": [dict(zip(app_constants.AF_TASKS_KEYS, task)) for task in tasks] } 
    else:
      return app_constants.DNF_RESPONSE

  @webapp.put("/api/1.0/<sessionUUID>/task")
  def entrypoint_insert_task(sessionUUID):
    if not user.isLoggedIn(sessionUUID):
      return app_constants.PLEASE_LOGIN

    userData = {}
    try:
      userData = request.get_json(force=True, cache=True)
    except:
      trace('Unable to process the incoming request. Please check your request body.')
      return {"status": "invalid request" }, 400

    if not userData.get(app_constants.AF_TASKS_INPUT_KEYS['userId'], ''):
        return {"status": "invalid request. userId is required." }, 400
    
    if userData:  
      values = create_tasks_tuple(userData)
      try:
        mycursor.execute(app_constants.SQL_INSERT_TASK, values)
        mydb.commit() 

        if mycursor.rowcount > 0:
          trace(f"Saved recoed in database with task id of {mycursor.lastrowid}")
        else:
          trace("No record is saved in database.")
          
      except:
        trace('An error has occured while inserting the task in the database.')
        return {"status": "Unexpected error occured." }, 500
      

    return {"status": "Task saved." }, 201

  @webapp.get("/api/1.0/<sessionUUID>/task/<taskId>")
  def entrypoint_show_task(sessionUUID, taskId):
    logged_in_user = user.isLoggedIn(sessionUUID)
    if not logged_in_user:
      return app_constants.PLEASE_LOGIN
    
    if taskId is None or str(taskId).strip() == "":
      return { "status": "error", "message": "taskId is required." }, 400
    
    task = getTask(taskId, logged_in_user)
    
    if task is not None:
      return { "status": "ok", "task": task }
    else:
      return app_constants.DNF_RESPONSE

  @webapp.delete("/api/1.0/<sessionUUID>/task/<taskId>")
  def entrypoint_remove_task(sessionUUID, taskId):
    logged_in_user = user.isLoggedIn(sessionUUID)
    if not logged_in_user:
      return app_constants.PLEASE_LOGIN

    deleted_rowcount = -1

    if taskId is None or not str(taskId).isdigit():
      return app_constants.DNF_RESPONSE
  
    try:
      if logged_in_user["is_admin"]:
        mycursor.execute(app_constants.SQL_DELETE_TASK, [taskId])
      else:
        mycursor.execute(app_constants.SQL_DELETE_TASK + " AND userId = %s", [taskId, logged_in_user["id"]])
      deleted_rowcount = mycursor.rowcount
      trace(f"Deleted task for record {taskId}.")
    except:
      trace("Error while deleting task(s) from database")
      deleted_rowcount = 0
      
    if deleted_rowcount > 0:
      return { "status": "ok" }
    else:
      return app_constants.DNF_RESPONSE

  @webapp.post("/api/1.0/<sessionUUID>/task/<taskId>")
  def entrypoint_edit_task(sessionUUID, taskId):
    logged_in_user = user.isLoggedIn(sessionUUID)
    if not logged_in_user:
      return app_constants.PLEASE_LOGIN

    userData = {}
    try:
      userData = request.get_json(force=True, cache=True)
    except:
      trace('Unable to process the incoming request. Please check your request body.')
      return {"status": "invalid request" }, 400
    
    if not userData.get(app_constants.AF_TASKS_INPUT_KEYS['userId'], ''):
        return {"status": "invalid request. userId is required." }, 400
    
    if userData:
      type, info = create_update_sql(userData, taskId, logged_in_user)

    print(info[0])
    if type == "ERROR":
      return info
    else:
      try:
        mycursor.execute(info[0], info[1])
        mydb.commit() 

        if mycursor.rowcount > 0:
          trace(f"Updated recoed in database with task id of {taskId}")
          return {"status": "success", "message": f"Task {taskId} updated."}
        else:
          trace(f"No task found with id {taskId} or no changes were made.")
          return {"status": "warning", "message": f"No task with id {taskId} found or no changes applied."}
      except:
        trace('An error has occured while inserting the task in the database.')
        return {"status": "Unexpected error occured." }, 500
      

  @webapp.get("/api/1.0/<sessionUUID>/task/<taskId>/result")
  def entrypoint_return_result(sessionUUID, taskId):
    logged_in_user = user.isLoggedIn(sessionUUID)
    if not logged_in_user:
      return app_constants.PLEASE_LOGIN

    task = getTask(taskId,logged_in_user)
    if task is not None:
      fName = os.path.join("results",f"{task['userId']}",f"{task['id']}.zip")
      if os.path.exists(fName):
        return send_from_directory(
            directory="..", path=fName, as_attachment=True
        )
      
      return { "status": "Result File Not Found" }, 404
    else:
      return app_constants.DNF_RESPONSE

  @webapp.get("/api/1.0/<sessionUUID>/task/<taskId>/log")
  def entrypoint_return_log(sessionUUID, taskId):
    logged_in_user = user.isLoggedIn(sessionUUID)
    if not logged_in_user:
      return app_constants.PLEASE_LOGIN

    task = getTask(taskId, logged_in_user)
    if task is not None:
      fName = os.path.join("results",f"{task['userId']}",f"{task['id']}.log")
      if os.path.exists(fName):
        return send_from_directory(
            directory="..", path=fName, as_attachment=True, mimetype="application/txt"
        )
      
      return { "status": "Log File Not Found" }, 404
    else:
      return app_constants.DNF_RESPONSE


def create_tasks_tuple(input_data):
    const_input_keys = app_constants.AF_TASKS_INPUT_KEYS

    enabled_value = input_data.get(const_input_keys['enabled'], 0)
    user_id_value = input_data[const_input_keys['userId']]

    task_name_value = input_data.get(const_input_keys['task_name'],'')
    user_comment_value = input_data.get(const_input_keys['user_comment'],'')
    fasta_data_value = input_data.get(const_input_keys['fasta'],'')
    model_preset_value = input_data.get(const_input_keys['preset'],'')

    full_dbs_value = input_data.get(const_input_keys['dbs'], 1) 
    models_to_relax_value = input_data.get(const_input_keys['models_to_relax'], 2)
    enable_gpu_relax_value = input_data.get(const_input_keys['gpu_relax'], 1)
    max_template_data_value = input_data.get(const_input_keys['template_date'], '')

    values = (
        enabled_value,
        user_id_value,
        task_name_value,
        user_comment_value,
        fasta_data_value,
        model_preset_value,
        full_dbs_value,
        models_to_relax_value,
        enable_gpu_relax_value,
        max_template_data_value
    )

    return values

def create_update_sql(userData, taskId, logged_in_user):
  set_clauses = []
  values = []
  
  for json_key, updated_value in userData.items():
    db_column_name = app_constants.AF_TASKS_INPUT_KEYS_TO_DB.get(json_key)

    if db_column_name and db_column_name in app_constants.ALLOWED_UPDATE_FIELDS:
      set_clauses.append(f"{db_column_name} = %s")
      values.append(updated_value)
  
  if not set_clauses:
    return ("ERROR", ({"status": "error", "message": "No valid fields provided for update."},400))
  
  sql = f"UPDATE af_tasks SET {', '.join(set_clauses)} " + "WHERE id = %s"
  values.append(taskId)

  if logged_in_user["is_admin"]:
     modified_sql = sql 
  else:
    modified_sql = sql + " AND userId = %s"
    values.append(logged_in_user["id"])
  return ("SQL", (modified_sql, values))