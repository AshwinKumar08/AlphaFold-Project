import mysql.connector
import time
import sys
from random import randint
from os import mkdir
from os.path import isdir
import zipfile

global mydb
mydb = None

def dbUp():
    global mydb
    mydb = mysql.connector.connect(
          host="af_db",
          user="frontend",
          password="frontend-secret-password",
          database="af-frontend"
          )

def dbDown():
    global mydb
    mydb.close()
    mydb = None


def trace(text):
    print(text, file=sys.stderr)

def addProcessRow(taskId, userId):
    trace(f"add task #{taskId} for user {userId}")
    taskId = int(taskId)
    userId = int(userId)
    mycursor = mydb.cursor()

    sql = "INSERT INTO af_results (id, state, results_file, log_file) VALUES (%s, %s, %s, %s)"
    val = (taskId, 0, f"{userId}/{taskId}.zip", f"{userId}/{taskId}.log")
    mycursor.execute(sql, val)

    mydb.commit()


def initNewTasks():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id, userId FROM af_tasks where id not in (select id from af_results)")
    myresult = mycursor.fetchall()
    
    for (i, u) in myresult:
        addProcessRow(i, u)

def getNextTask():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT r.id, r.results_file, r.log_file, t.userId FROM af_results r left join af_tasks t on (t.id = r.id) where r.state = 0 and t.enabled = 1")
    myresult = mycursor.fetchall()
    
    for x in myresult:
        return list(x)

    return None

def updateTaskState(taskId, state):
    trace(f"set task #{taskId} to state {state}")
    mycursor = mydb.cursor()
    sql = "UPDATE af_results set state=%s where id=%s"
    val = (int(state), int(taskId))
    mycursor.execute(sql, val)
    mydb.commit()


def mkUserDir(userId):
    d = "/app"
    trace("Test dir: " + d)
    if not isdir(d):
        trace("create dir: " + d)
        mkdir(d)

    d += "/results"
    trace("Test dir: " + d)
    if not isdir(d):
        trace("create dir: " + d)
        mkdir(d)

    d += f"/{userId}"
    trace("Test dir: " + d)
    if not isdir(d):
        trace("create dir: " + d)
        mkdir(d)



taskStateInProgress = 1
taskStateDone = 2

time.sleep(10)

while True:
    dbUp()
    initNewTasks()
    t = getNextTask()
    if t is not None:
        (taskId, zipFile, logFile, userId) = t
        taskId = int(taskId)
        userId = int(userId)
        logFile = f"/app/results/{userId}/{taskId}.log"
        zipFile = f"/app/results/{userId}/{taskId}.zip"
        trace(f"Start task: {t}")
        mkUserDir(userId)
        with open(logFile, "wt") as f:
            print(f"Started task #{taskId}\n", file = f)
        
        updateTaskState(taskId, taskStateInProgress)
        
        duration = 30 + randint(0, 120)
        time.sleep(duration)

        with open(logFile, "at") as f:
            print(f"Finished task #{taskId} after {duration} seconds\n", file = f)

        with zipfile.ZipFile(zipFile, "w") as f:
            f.writestr("example.txt", "here would be some data.\n")

        updateTaskState(taskId, taskStateDone)
        trace(f"finished task #{taskId}")
    dbDown()
    time.sleep(10)
