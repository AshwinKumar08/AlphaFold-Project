import datetime
import sys
from flask import request
from app.dbUtil import create_secure_password, verify_password
import app.constants as app_constants
import time

mycursor = None
mydb = None
try:
  from app.dbUtil import getDbInstance
  mydb = getDbInstance()
  mycursor = mydb.cursor()
except:
  print("Error occured while connecting to the DB")


global users
global sessions
global nextSessionNr
global serverId

serverId = int(time.time())

fakeUser1 = { "id": 1, "name": "test_user", "is_admin": 0 }
fakeUser2 = { "id": 2, "name": "test_admin", "is_admin": 1 }

users = [ fakeUser1, fakeUser2 ]

sessions = {}
nextSessionNr = 1

def trace(text):
    print(text, file=sys.stderr)

def isLoggedIn(sessionUUID):
  # TODO: actually check if the current user is logged in
  user = getUserFromSession(sessionUUID)
  return user

def isAdmin(sessionUUID):
  # TODO: actually check if the current user is an administrator
  user = getUserFromSession(sessionUUID)
  if user is not None:
    return user["is_admin"] == 1

  return False

def getUserFromSession(sessionUUID):
  if sessionUUID is not None:
    try:
      mycursor.execute(app_constants.SQL_SELECT_ACTIVE_SESSION_BY_ID, [sessionUUID])
      user_session = mycursor.fetchone()
      trace(f"Session found : {user_session}")

      if user_session and user_session[4] == app_constants.SESSION_ACTIVE:
        return {"id":user_session[1],"name": user_session[5],"is_admin": user_session[-1]}
      else:
        mycursor.execute(app_constants.SQL_DELETE_INACTIVE_SESSIONS)
      
    except:
      trace(f"Error while fetching user session for session id: {sessionUUID}")
  
  return None

def getUser(userId):
  if userId is None or not str(userId).isdigit():
    return None
  
  userId = int(userId)

  try:
    mycursor.execute(app_constants.SQL_SELECT_USER_BY_ID, [userId])
    user = mycursor.fetchone()
    trace(f"fetched successfully for user: {userId}")
    
  except:
    trace(f"Error while fetching user from database for user id: {userId}")
    user = None

  return user

def getUserByName(userName,pw):
  if userName is None or not str(userName):
    return None
  
  if pw is None or not str(pw):
    return None
  
  userName = str(userName)

  try:
    mycursor.execute(app_constants.SQL_SELECT_USER_BY_NAME, [userName])
    user = mycursor.fetchone()
    trace(f"fetched successfully for user: {userName}")
    
  except:
    trace(f"Error while fetching user from database for user name: {userName}")
    return None

  try:
    if verify_password(pw, user[2]):
      return user
  except:
    return None

def newSession(userId, userDB):
  global nextSessionNr
  global sessions
  global serverId
  user = userDB
  if (user or userId) is None:
    return None

  sessionId = f"{serverId}-{nextSessionNr}-{userId}"

  
  sessoin_expires_at = datetime.datetime.now() + datetime.timedelta(hours=app_constants.SESSION_EXPIRY_HOURS)
  insert_data = (sessionId, userId, sessoin_expires_at, 1)
  
  try:
    mycursor.execute(app_constants.SQL_INSERT_SESSION, insert_data)
    mydb.commit()
    trace(f"Session Created and stored: {sessionId} for user: {userId}")
    
  except:
    trace(f"Error while creating user session: {userId}")
    return None

  # sessions[sessionId] = { "sessionId" : sessionId, "userId" : userId }
  nextSessionNr += 1

  return sessionId

def getListOfUsers():
  try:
    mycursor.execute(app_constants.SQL_SELECT_USERS)
    users = mycursor.fetchall()
  except:
    trace("Error while fetching users from database")
    users = []

  if users and len(users) > 0:
    return [dict(zip(app_constants.AF_USERS_KEYS, user)) for user in users] 
  else:
    return app_constants.DNF_RESPONSE

def getListOfSessions():
  try:
    mycursor.execute(app_constants.SQL_SELECT_SESSIONS)
    user_sess = mycursor.fetchall()
  except:
    trace("Error while fetching sessions from database")
    user_sess = []

  if user_sess and len(user_sess) > 0:
    return [dict(zip(app_constants.AF_USERS_KEYS, user_ses)) for user_ses in user_sess] 
  else:
    return app_constants.DNF_RESPONSE

def doLogin(userName, pw):
  user = getUserByName(userName, pw)
  if user is not None:
    return newSession(user[0], user)
  return None

def doLogout(sessionUUID):
  try:
    mycursor.execute(app_constants.SQL_UPDATE_INACTIVE_SESSION, [sessionUUID])
    mydb.commit()
    return True
  except:
    trace('Unable to log out session')
  return False
  



def createEntrypoints(webapp):
  @webapp.get("/api/1.0/<sessionUUID>/user")
  def entrypoint_list_users(sessionUUID):
    if not isLoggedIn(sessionUUID) or not isAdmin(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    return {"status": "ok", "users": getListOfUsers() }

  @webapp.put("/api/1.0/<sessionUUID>/user")
  def entrypoint_insert_user(sessionUUID):
    if not isLoggedIn(sessionUUID) or not isAdmin(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    sendData = request.get_json(force=True)
    return {"status": "temporary not available" }, 500


  @webapp.get("/api/1.0/<sessionUUID>/user/<userIdText>")
  def entrypoint_show_user(sessionUUID, userIdText):
    if not isLoggedIn(sessionUUID) or not isAdmin(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return { "status": "not found'" }, 404

    # TODO: Find user in database
    user = getUser(userId)
    if user is not None:
      return { "status": "ok", "user": user }
    else:
      return { "status": "not found" }, 404


  @webapp.delete("/api/1.0/<sessionUUID>/user/<userIdText>")
  def entrypoint_remove_user(sessionUUID, userIdText):
    if not isLoggedIn(sessionUUID) or not isAdmin(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return { "status": "not found'" }, 404

    # TODO: Remove the user in database
    user = getUser(userId)
    if user is not None:
      return { "status": "ok" }
    else:
      return { "status": "not found" }, 404


  @webapp.post("/api/1.0/<sessionUUID>/user/<userIdText>")
  def entrypoint_edit_user(sessionUUID, userIdText):
    if not isLoggedIn(sessionUUID) or not isAdmin(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return { "status": "not found'" }, 404

    sendData = request.get_json(force=True)
    # TODO: Edit the user in database
    user = getUser(userId)
    if user is not None:
      return { "status": "ok" }
    else:
      return { "status": "not found" }, 404


  @webapp.post("/api/1.0/login")
  def entrypoint_login():
    # TODO: actually log in
    receivedData = request.get_json(force=True)
    sessionUUID = None
   
    if "userName" in receivedData and "pass" in receivedData:
      sessionUUID = doLogin(receivedData["userName"], receivedData["pass"])

    if sessionUUID is not None and isLoggedIn(sessionUUID):
      return { "status": "ok", "sessionUUID": sessionUUID }
    else:
      return { "status": "failed to log in" }, 403

  @webapp.get("/api/1.0/<sessionUUID>/logout")
  def entrypoint_logout(sessionUUID):
    if doLogout(sessionUUID):
      return { "status": "OK" }
    else:
      return ({ "status": "error" }, 500)
    

def registerUser(userName, password):
    try:
      mycursor.execute(app_constants.SQL_SELECT_USER_BY_NAME, [userName])
      if mycursor.fetchone():
          return False

      hashed_pw = create_secure_password(password)
      mycursor.execute(app_constants.SQL_INSERT_USER_BY_NAME, [userName, hashed_pw, 0])
      mydb.commit()
      return True
    except Exception as e:
      trace(f"Error during registration: {e}")
      return False
    

def deleteUser(userId):
    try:
      mycursor.execute(app_constants.SQL_DELETE_USER_BY_ID, [userId])
      mydb.commit()
      return True
    except Exception as e:
      trace(f"Error deleting user: {e}")
      return False
