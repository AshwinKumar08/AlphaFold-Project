import os
import app.user as user
from flask import request

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


def getTask(taskId):
  # TODO: actually search the task in the database
  if taskId == 1:
    return fakeTask1
  elif taskId == 2:
    return fakeTask2
  else:
    return None


def createEntrypoints(webapp):
  @webapp.get("/<sessionUUID>/task")
  def entrypoint_list_tasks(sessionUUID):
    if not user.isLoggedIn(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    # TODO: Read tasks from database
    return {"status": "ok", "tasks": fakeTasks }

  @webapp.put("/<sessionUUID>/task")
  def entrypoint_insert_task(sessionUUID):
    if not user.isLoggedIn(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    sendData = request.get_json(force=True)
    # TODO: store the new task
    return {"status": "temporary not available" }, 500


  @webapp.get("/<sessionUUID>/task/<taskIdText>")
  def entrypoint_show_task(sessionUUID, taskIdText):
    if not user.isLoggedIn(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    taskId = int(taskIdText)
    if f"{taskId}" != taskIdText:
      return { "status": "not found'" }, 404

    task = None
    # TODO: Find task in database
    task = getTask(taskId)
    if task is not None:
      return { "status": "ok", "task": task }
    else:
      return { "status": "not found" }, 404


  @webapp.delete("/<sessionUUID>/task/<taskIdText>")
  def entrypoint_remove_task(sessionUUID, taskIdText):
    if not user.isLoggedIn(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    taskId = int(taskIdText)
    if f"{taskId}" != taskIdText:
      return { "status": "not found'" }, 404

    # TODO: Remove the task in database
    task = getTask(taskId)
    if task is not None:
      return { "status": "ok" }
    else:
      return { "status": "not found" }, 404


  @webapp.post("/<sessionUUID>/task/<taskIdText>")
  def entrypoint_edit_task(sessionUUID, taskIdText):
    if not user.isLoggedIn(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    taskId = int(taskIdText)
    if f"{taskId}" != taskIdText:
      return { "status": "not found'" }, 404

    sendData = request.get_json(force=True)
    # TODO: Remove the task in database
    task = getTask(taskId)
    if task is not None:
      return { "status": "ok" }
    else:
      return { "status": "not found" }, 404


  @webapp.get("/<sessionUUID>/task/<taskIdText>/result")
  def entrypoint_return_result(sessionUUID, taskIdText):
    if not user.isLoggedIn(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    taskId = int(taskIdText)
    if f"{taskId}" != taskIdText:
      return { "status": "not found'" }, 404

    # TODO: Remove the task in database
    task = getTask(taskId)
    if task is not None:
      rData = None
      fName = f"data/{task['userId']}/{task['id']}.zip"
      if os.path.exists(fName):
        with open(fName) as f:
          return f.read() 

      return { "status": "temporary not available" }, 500
    else:
      return { "status": "not found" }, 404



  @webapp.get("/<sessionUUID>/task/<taskIdText>/log")
  def entrypoint_return_log(sessionUUID, taskIdText):
    if not user.isLoggedIn(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    taskId = int(taskIdText)
    if f"{taskId}" != taskIdText:
      return { "status": "not found'" }, 404

    # TODO: Remove the task in database
    task = getTask(taskId)
    if task is not None:
      rData = None
      fName = f"data/{task['userId']}/{task['id']}.zip"
      if os.path.exists(fName):
        with open(fName) as f:
          return f.read() 

      return { "status": "temporary not available" }, 500
    else:
      return { "status": "not found" }, 404


