from flask import request

fakeUser1 = { "id": 1, "name": "test_user", "is_admin": 0 }
fakeUser2 = { "id": 2, "name": "test_admin", "is_admin": 1 }

users = { 1: fakeUser1, 2: fakeUser2 }

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
  if sessionUUID is not None and sessionUUID in sessions:
    s = sessions[sessionUUID]
    return getUser(s["userId"])
  return None

def getUser(userId):
  # TODO: actually search the user in the database
  if userId in users:
    return users[userId]
  else:
    return None

def getUserByName(userName):
  # TODO: actually search the user in the database
  for k in users.keys():
    u = users[k]
    if u["name"] == userName:
      return u

  return None

def newSession(userId):
  # TODO: implement session management
  global nextSessionNr
  user = getUser(userId)
  if user is None:
    return None

  sessionId = f"{nextSessionNr}-{userId}"
  nextSessionNr += 1

  s = { "sessionId" : sessionId, "userId" : userId }
  sessions[sessionId] = s
  return sessionId


def createEntrypoints(webapp):
  @webapp.get("/<sessionUUID>/user")
  def entrypoint_list_users(sessionUUID):
    if not isLoggedIn(sessionUUID) or not isAdmin(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    # TODO: Read users from database
    return {"status": "ok", "users": users }

  @webapp.put("/<sessionUUID>/user")
  def entrypoint_insert_user(sessionUUID):
    if not isLoggedIn(sessionUUID) or not isAdmin(sessionUUID):
      return { "status": "please login", "url": ["/login"] }, 403

    sendData = request.get_json(force=True)
    # TODO: store the new user
    return {"status": "temporary not available" }, 500


  @webapp.get("/<sessionUUID>/user/<userIdText>")
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


  @webapp.delete("/<sessionUUID>/user/<userIdText>")
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


  @webapp.post("/<sessionUUID>/user/<userIdText>")
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


  @webapp.get("/login")
  def entrypoint_login():
    # TODO: actually log in
    sendData = request.get_json(force=True)
    sessionUUID = None
    if "userName" in sendData:
      user = getUserByName(sendData["userName"])
      if user is not None:
        sessionUUID = newSession(user["id"])

    if sessionUUID is not None and isLoggedIn(sessionUUID):
      return { "status": "ok", "sessionUUID": sessionUUID }
    else:
      return { "status": "failed to log in" }, 403



  @webapp.get("/<sessionUUID>/logout")
  def entrypoint_logout(sessionUUID):
    if sessionUUID in sessions:
      del sessions[sessionUUID]
    # TODO: actually log out
    return { "status": "OK" }


