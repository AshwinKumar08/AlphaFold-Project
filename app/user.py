from flask import request

import time

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

def isLoggedIn(sessionUUID):
  # TODO: actually check if the current user is logged in
  user = getUserFromSession(sessionUUID)
  return user is not None

def isAdmin(sessionUUID):
  # TODO: actually check if the current user is an administrator
  user = getUserFromSession(sessionUUID)
  if user is not None:
    return user["is_admin"] == 1

  return False

def getUserFromSession(sessionUUID):
  # TODO: actually search the session and the user in the database
  global sessions
  if sessionUUID is not None and sessionUUID in sessions:
    s = sessions[sessionUUID]
    return getUser(s["userId"])
  return None

def getUser(userId):
  # TODO: actually search the user in the database
  global users
  userId = int(userId)
  for u in users:
    if u["id"] == userId:
      return u
  return None

def getUserByName(userName):
  # TODO: actually search the user in the database
  global users
  for u in users:
    if u["name"] == userName:
      return u

  return None

def newSession(userId):
  # TODO: implement session management
  global nextSessionNr
  global sessions
  global serverId
  user = getUser(userId)
  if user is None:
    return None

  sessionId = f"{serverId}-{nextSessionNr}-{userId}"
  nextSessionNr += 1

  s = { "sessionId" : sessionId, "userId" : userId }
  sessions[sessionId] = s
  return sessionId

def getListOfUsers():
  global users
  # TODO: Lookup database
  return users

def getListOfSessions():
  global sessions
  # TODO: Lookup database
  return sessions

def doLogin(userName):
  # TODO: implement this
  user = getUserByName(userName)
  if user is not None:
    return newSession(user["id"])
  return None

def doLogout(sessionUUID):
  # TODO: implement this
  global sessions
  if sessionUUID in sessions:
    del sessions[sessionUUID]


def createEntrypoints(webapp):
  @webapp.get("/api/1.0/<sessionUUID>/user")
  def entrypoint_list_users(sessionUUID):
    if not isLoggedIn(sessionUUID) or not isAdmin(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    # TODO: Read users from database
    return {"status": "ok", "users": getListOfUsers() }

  @webapp.put("/api/1.0/<sessionUUID>/user")
  def entrypoint_insert_user(sessionUUID):
    if not isLoggedIn(sessionUUID) or not isAdmin(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    sendData = request.get_json(force=True)
    # TODO: store the new user
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


  @webapp.get("/api/1.0/login")
  def entrypoint_login():
    # TODO: actually log in
    sendData = request.get_json(force=True)
    sessionUUID = None
    if "userName" in sendData:
      sessionUUID = doLogin(sendData["userName"])

    if sessionUUID is not None and isLoggedIn(sessionUUID):
      return { "status": "ok", "sessionUUID": sessionUUID }
    else:
      return { "status": "failed to log in" }, 403



  @webapp.get("/api/1.0/<sessionUUID>/logout")
  def entrypoint_logout(sessionUUID):
    doLogout(sessionUUID)
    # TODO: actually log out
    return { "status": "OK" }


