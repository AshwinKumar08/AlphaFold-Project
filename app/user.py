import sys
from flask import request
from app.dbUtil import create_secure_password, verify_password
import app.constants as app_constants
from datetime import datetime, timedelta
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
  # Check if the current user is logged in
  user = getUserFromSession(sessionUUID)
  return user

def isAdmin(sessionUUID):
  # Check if the current user is an administrator
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

      if user_session and user_session[4] == app_constants.SESSION_ACTIVE and user_session[7] == 1:  # Check enabled
        return {"id":user_session[1],"name": user_session[5],"is_admin": user_session[6], "enabled": user_session[7]}
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
    trace(f"User data fetched: {user}")
    
  except Exception as e:
    trace(f"Error while fetching user from database for user id: {userId}: {e}")
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

  if user[4] != 1:  # Check enabled
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

  
  sessoin_expires_at = datetime.now() + timedelta(hours=app_constants.SESSION_EXPIRY_HOURS)
  insert_data = (sessionId, userId, sessoin_expires_at, 1)
  
  try:
    mycursor.execute(app_constants.SQL_INSERT_SESSION, insert_data)
    mydb.commit()
    trace(f"Session Created and stored: {sessionId} for user: {userId}")
    
  except:
    trace(f"Error while creating user session: {userId}")
    return None

  nextSessionNr += 1

  return sessionId

def getListOfUsers(search_query=None, role_filter=None, status_filter=None, date_from=None, date_to=None):
  try:
    sql = app_constants.SQL_SELECT_USERS
    conditions = []
    params = []
    
    # Add search filter
    if search_query and search_query.strip():
      conditions.append("LOWER(name) LIKE %s")
      params.append(f"%{search_query.lower()}%")
    
    # Add role filter
    if role_filter == "admin":
      conditions.append("is_admin = 1")
    elif role_filter == "regular":
      conditions.append("is_admin = 0")
    
    # Add status filter
    if status_filter == "enabled":
      conditions.append("enabled = 1")
    elif status_filter == "disabled":
      conditions.append("enabled = 0")
    
    # Add date range filter
    if date_from and date_from.strip():
      conditions.append("last_login >= %s")
      params.append(date_from)
    
    if date_to and date_to.strip():
      conditions.append("last_login <= %s")
      params.append(date_to + " 23:59:59")  # Include entire day
    
    # Combine all conditions
    if conditions:
      sql += " WHERE " + " AND ".join(conditions)
    
    mycursor.execute(sql, params if params else None)
    users = mycursor.fetchall()
  except Exception as e:
    trace(f"Error while fetching users from database: {e}")
    users = []

  if users and len(users) > 0:
    return [dict(zip(app_constants.AF_USERS_KEYS, user)) for user in users] 
  else:
    return []


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
    if not userName or not pw:
        return {"success": False, "error": "Username and password are required"}
    
    # Check if user exists
    try:
        mycursor.execute(app_constants.SQL_SELECT_USER_BY_NAME, [userName])
        user = mycursor.fetchone()
    except Exception as e:
        trace(f"Database error during login: {e}")
        return {"success": False, "error": "Database error, please try again later"}
    
    # If User is not found
    if not user:
       return {"success": False, "error": "User not found. You need to have an account to access the project."}
    
    user_id = user[0]
    
    # If User exists but account is disabled
    if user[4] != 1:  # Check enabled field
        return {"success": False, "error": "Account is disabled. Please contact an administrator."}
    
    # Lock account after specific unsuccessful logins
    try:
        mycursor.execute(app_constants.SQL_SELECT_LOGIN_ATTEMPTS, [user_id])
        row = mycursor.fetchone()

        failed_attempts = row[0] if row else 0
        locked_until = row[1] if row else None

        if locked_until:
            if isinstance(locked_until, str):
                locked_until = datetime.strptime(
                    locked_until, "%Y-%m-%d %H:%M:%S"
                )

            if locked_until > datetime.now():
                remaining_seconds = int(
                    (locked_until - datetime.now()).total_seconds()
                )
                print("DEBUG LOCKED remaining_seconds =", remaining_seconds)

                return {
                    "success": False,
                    "error": "Account locked. Try again later.",
                    "remaining_seconds": remaining_seconds
                }

    except Exception as e:
        trace(f"Lockout check failed: {e}")

    # Verify password
    try:
        if not user[2]:
            trace("Stored password hash is empty")
            return {"success": False, "error": "Account configuration error"}

        if verify_password(pw, user[2]):
          try:
                mycursor.execute(
                    app_constants.SQL_RESET_LOGIN_ATTEMPTS,
                    [user_id]
                )
                mydb.commit()
          except Exception as e:
                trace(f"Failed to reset login attempts: {e}")
          try:
                mycursor.execute(
                    app_constants.SQL_UPDATE_USER_LAST_LOGIN,
                    [user_id]
                )
                mydb.commit()
          except Exception as e:
                trace(f"Failed to update last_login: {e}")

          sessionUUID = newSession(user_id, user)
          if not sessionUUID:
                return {"success": False, "error": "Session creation failed"}

          return {
                "success": True,
                "sessionUUID": sessionUUID,
                "user": user
            }
        failed_attempts += 1
        if failed_attempts >= app_constants.MAX_FAILED_ATTEMPTS:
            locked_until = datetime.now() + timedelta(
                minutes=app_constants.LOCKOUT_DURATION_MINUTES
            )
            mycursor.execute(
                app_constants.SQL_LOCK_USER_ACCOUNT,
                [
                    failed_attempts,
                    locked_until.strftime("%Y-%m-%d %H:%M:%S"),
                    user_id
                ]
            )
            mydb.commit()
            remaining_seconds = int(
                (locked_until - datetime.now()).total_seconds()
            )
            print("DEBUG LOCK SET remaining_seconds =", remaining_seconds)
            return {
                "success": False,
                "error": "Account locked. Try again later.",
                "remaining_seconds": remaining_seconds
            }
        else:
            mycursor.execute(
                app_constants.SQL_INCREMENT_LOGIN_ATTEMPTS,
                [failed_attempts, user_id]
            )
            mydb.commit()
            return {
                "success": False,
                "error": "Username found, but password is incorrect."
            }
    except Exception as e:
        trace(f"Password verification error: {e}")
        trace(f"DEBUG pw={pw}")
        trace(f"DEBUG stored_hash={user[2]}")
        return {"success": False, "error": "Password verification failed"}

def doLogout(sessionUUID):
  try:
    mycursor.execute(app_constants.SQL_UPDATE_INACTIVE_SESSION, [sessionUUID])
    mydb.commit()
    return True
  except:
    trace('Unable to log out session')
  return False
  
# User Profile
def getUserOwnProfile(sessionUUID):
    user = getUserFromSession(sessionUUID)
    if user:
        return getUser(user["id"])
    return None

def updateOwnPassword(sessionUUID, current_password, new_password):
    user = getUserFromSession(sessionUUID)
    if not user:
        return False
    
    try:
        mycursor.execute(app_constants.SQL_SELECT_USER_BY_ID, [user["id"]])
        db_user = mycursor.fetchone()
        if not db_user or not verify_password(current_password, db_user[2]):
            return False
    except:
        return False
    
    return updateUserPassword(user["id"], new_password)

# MESSAGE FUNCTIONS
def sendMessage(sender_id, recipient_id, subject, message, message_type='user'):
    try:
        mycursor.execute(app_constants.SQL_INSERT_MESSAGE, 
                        [sender_id, recipient_id, subject, message, message_type])
        mydb.commit()
        return True
    except Exception as e:
        trace(f"Error sending message: {e}")
        return False

def getUserMessages(user_id):
    try:
        mycursor.execute(app_constants.SQL_SELECT_USER_MESSAGES, [user_id])
        messages = mycursor.fetchall()
        return messages if messages else []
    except Exception as e:
        trace(f"Error fetching messages: {e}")
        return []

def markMessageRead(message_id):
    try:
        mycursor.execute(app_constants.SQL_MARK_MESSAGE_READ, [message_id])
        mydb.commit()
        return True
    except:
        return False

def getUnreadCount(user_id):
    try:
        mycursor.execute(app_constants.SQL_COUNT_UNREAD_MESSAGES, [user_id])
        count = mycursor.fetchone()[0]
        return count
    except:
        return 0

def createSupportTicket(user_id, subject, description, priority='medium'):
    try:
        trace(f"Creating support ticket for user {user_id}: {subject}")
        mycursor.execute(app_constants.SQL_INSERT_SUPPORT_TICKET,
                        [user_id, subject, description, priority])
        mydb.commit()
        ticket_id = mycursor.lastrowid
        trace(f"Support ticket created successfully. ID: {ticket_id}")
        return True
    except Exception as e:
        trace(f"Error creating ticket: {e}")
        import traceback
        trace(f"Full traceback: {traceback.format_exc()}")
        return False

def getUserTickets(user_id):
    try:
        trace(f"Fetching all tickets for display to user {user_id}")
        dict_cursor = mydb.cursor(dictionary=True)
        dict_cursor.execute("""
            SELECT t.id, t.user_id, t.subject, t.description, t.status, t.priority, 
                   t.created_at, t.updated_at, u.name as user_name
            FROM af_support_tickets t
            JOIN af_users u ON t.user_id = u.id
            ORDER BY t.created_at DESC
        """)
        tickets = dict_cursor.fetchall()
        dict_cursor.close()
        trace(f"Found {len(tickets)} tickets")
        trace(f"Tickets: {tickets}")
        return tickets
    except Exception as e:
        trace(f"Error fetching user tickets: {e}")
        import traceback
        trace(f"Full traceback: {traceback.format_exc()}")
        return []
    
def getAllTickets():
    try:
        trace("Fetching all tickets (admin view)")
        dict_cursor = mydb.cursor(dictionary=True)
        dict_cursor.execute("""
            SELECT t.id, t.user_id, t.subject, t.description, t.status, t.priority, 
                   t.created_at, t.updated_at, u.name as user_name
            FROM af_support_tickets t
            JOIN af_users u ON t.user_id = u.id
            ORDER BY t.created_at DESC
        """)
        tickets = dict_cursor.fetchall()
        dict_cursor.close()
        trace(f"Found {len(tickets)} total tickets")
        trace(f"Tickets: {tickets}")
        return tickets
    except Exception as e:
        trace(f"Error fetching all tickets: {e}")
        import traceback
        trace(f"Full traceback: {traceback.format_exc()}")
        return []
    
def deleteMessage(message_id, user_id):
    """Delete a message if it belongs to the user"""
    try:
        # First verify the message belongs to this user
        mycursor.execute("SELECT recipient_id FROM af_messages WHERE id = %s", [message_id])
        msg = mycursor.fetchone()
        if msg and msg[0] == user_id:
            mycursor.execute(app_constants.SQL_DELETE_MESSAGE, [message_id])
            mydb.commit()
            return True
        return False
    except Exception as e:
        trace(f"Error deleting message: {e}")
        return False

#Entry points start here
def createEntrypoints(webapp):
  @webapp.get("/api/1.0/<sessionUUID>/user")
  def entrypoint_list_users(sessionUUID):
    if not isLoggedIn(sessionUUID):
        return { "status": "please login", "url": ["/login"] }, 403

    if not isAdmin(sessionUUID):
        return { 
            "status": "admin access required", 
            "message": "Only administrators can list users." 
        }, 403
    
    # Search query from request parameters
    search_query = request.args.get("search", None)

    return {"status": "ok", "users": getListOfUsers() }
  

  @webapp.put("/api/1.0/<sessionUUID>/user")
  def entrypoint_insert_user(sessionUUID):
    if not isLoggedIn(sessionUUID):
        return { "status": "please login", "url": ["/login"] }, 403
    
    if not isAdmin(sessionUUID):
        return { 
            "status": "admin access required", 
            "message": "Only an admin can create new users." 
        }, 403

    sendData = request.get_json(force=True)
    return {"status": "temporary not available" }, 500


  @webapp.get("/api/1.0/<sessionUUID>/user/<userIdText>")
  def entrypoint_show_user(sessionUUID, userIdText):
    if not isLoggedIn(sessionUUID):
        return { "status": "please login", "url": ["/login"] }, 403
    
    if not isAdmin(sessionUUID):
        return { 
            "status": "admin access required", 
            "message": "Only an admin can view user details." 
        }, 403

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return { "status": "not found'" }, 404

    # Find user in database
    user = getUser(userId)
    if user is not None:
      return { "status": "ok", "user": user }
    else:
      return { "status": "not found" }, 404


  @webapp.delete("/api/1.0/<sessionUUID>/user/<userIdText>")
  def entrypoint_remove_user(sessionUUID, userIdText):
    if not isLoggedIn(sessionUUID):
        return { "status": "please login", "url": ["/login"] }, 403
    
    if not isAdmin(sessionUUID):
        return { 
            "status": "admin access required", 
            "message": "Only an admin can delete users." 
        }, 403

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return { "status": "not found'" }, 404

    # Remove the user in database
    user = getUser(userId)
    if user is not None:
      return { "status": "ok" }
    else:
      return { "status": "not found" }, 404


  @webapp.post("/api/1.0/<sessionUUID>/user/<userIdText>")
  def entrypoint_edit_user(sessionUUID, userIdText):
    if not isLoggedIn(sessionUUID):
        return { "status": "please login", "url": ["/login"] }, 403
    
    if not isAdmin(sessionUUID):
        return { 
            "status": "admin access required", 
            "message": "Only an admin can edit users." 
        }, 403

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return { "status": "not found'" }, 404

    sendData = request.get_json(force=True)
    if "enabled" in sendData:
        updateUserEnabled(userId, sendData["enabled"], sessionUUID)
    # Edit the user in database
    user = getUser(userId)
    if user is not None:
      return { "status": "ok" }
    else:
      return { "status": "not found" }, 404


  @webapp.post("/api/1.0/login")
  def entrypoint_login():
    receivedData = request.get_json(force=True)
    sessionUUID = None
    
    if "userName" in receivedData and "pass" in receivedData:
        login_result = doLogin(receivedData["userName"], receivedData["pass"])
        if login_result.get("success"):
            return { 
                "status": "ok", 
                "sessionUUID": login_result.get("sessionUUID"),
                "user": {
                    "id": login_result.get("user")[0],
                    "name": login_result.get("user")[1],
                    "is_admin": login_result.get("user")[3]
                }
            }
        else:
            response = { 
                "status": "failed", 
                "message": login_result.get("error", "Login failed")
            }
            if "remaining_seconds" in login_result:
                response["remaining_seconds"] = login_result["remaining_seconds"]
                
            return response, 403

    else:
        return { 
            "status": "failed", 
            "message": "Username and password are required"
        }, 400
    

  @webapp.get("/api/1.0/<sessionUUID>/logout")
  def entrypoint_logout(sessionUUID):
    if doLogout(sessionUUID):
      return { "status": "OK" }
    else:
      return ({ "status": "error" }, 500)
    
  @webapp.get("/api/1.0/<sessionUUID>/messages")
  def entrypoint_get_messages(sessionUUID):
    logged_user = isLoggedIn(sessionUUID)
    if not logged_user:
      return app_constants.PLEASE_LOGIN
    
    messages = getUserMessages(logged_user["id"])
    return {"status": "ok", "messages": messages}
  
  @webapp.post("/api/1.0/<sessionUUID>/messages/send")
  def entrypoint_send_message(sessionUUID):
    logged_user = isLoggedIn(sessionUUID)
    if not logged_user:
      return app_constants.PLEASE_LOGIN
    
    data = request.get_json()
    recipient_id = data.get("recipient_id")
    subject = data.get("subject", "")
    message = data.get("message")
    msg_type = 'admin' if logged_user["is_admin"] else 'user'
    
    if sendMessage(logged_user["id"], recipient_id, subject, message, msg_type):
      return {"status": "ok"}
    return {"status": "error"}, 500
  
  @webapp.post("/api/1.0/<sessionUUID>/support/ticket")
  def entrypoint_create_ticket(sessionUUID):
    logged_user = isLoggedIn(sessionUUID)
    if not logged_user:
      return app_constants.PLEASE_LOGIN
    
    data = request.get_json()
    if createSupportTicket(logged_user["id"], data["subject"], 
                          data["description"], data.get("priority", "medium")):
      return {"status": "ok"}
    return {"status": "error"}, 500

    

def registerUser(userName, password, is_admin: int = 0):
    try:
      mycursor.execute(app_constants.SQL_SELECT_USER_BY_NAME, [userName])
      if mycursor.fetchone():
          return False

      hashed_pw = create_secure_password(password)
      mycursor.execute(app_constants.SQL_INSERT_USER_BY_NAME, [userName, hashed_pw, int(is_admin), 1])
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

def updateUserRole(userId, isAdmin):
  try:
    mycursor.execute(app_constants.SQL_UPDATE_USER_ROLE, [int(isAdmin), int(userId)])
    mydb.commit()
    return True
  except Exception as e:
    trace(f"Error updating user role: {e}")
    return False
  
def updateUserName(userId, newName):
  try:
    # Validate
    if not newName or not str(newName).strip():
      trace("Invalid user name provided for update")
      return False

    newName = str(newName).strip()

    # Check duplicate name owned by other user
    mycursor.execute(app_constants.SQL_SELECT_USER_BY_NAME, [newName])
    row = mycursor.fetchone()
    if row and int(row[0]) != int(userId):
      trace("User name already exists for another user")
      return False

    mycursor.execute(app_constants.SQL_UPDATE_USER_NAME, [newName, int(userId)])
    mydb.commit()
    return True
  except Exception as e:
    trace(f"Error updating user name: {e}")
    return False

def updateUserPassword(userId, newPassword):
  try:
    if not newPassword or len(str(newPassword)) < 4:
      trace("Password too short or invalid")
      return False

    hashed = create_secure_password(str(newPassword))
    if not hashed:
      trace("Failed to hash new password")
      return False

    mycursor.execute(app_constants.SQL_UPDATE_USER_PASSWORD, [hashed, int(userId)])
    mydb.commit()
    return True
  except Exception as e:
    trace(f"Error updating user password: {e}")
    return False
  
def updateUserEnabled(userId, enabled, sessionUUID):
  if not isLoggedIn(sessionUUID) or not isAdmin(sessionUUID):
    trace("Non-admin attempted to enable/disable user")
    return False
  
  try:
    mycursor.execute(app_constants.SQL_UPDATE_USER_ENABLED, [int(enabled), int(userId)])
    mydb.commit()
    return True
  except Exception as e:
    trace(f"Error updating user enabled status: {e}")
    return False
  
def updateUserEmail(userId, email):
    try:
        mycursor.execute(app_constants.SQL_UPDATE_USER_EMAIL, [email, int(userId)])
        mydb.commit()
        return True
    except Exception as e:
        trace(f"Error updating user email: {e}")
        return False

def updateUserDOB(userId, dob):
    try:
        # Handle empty date
        dob_value = dob if dob else None
        mycursor.execute(app_constants.SQL_UPDATE_USER_DOB, [dob_value, int(userId)])
        mydb.commit()
        return True
    except Exception as e:
        trace(f"Error updating user date of birth: {e}")
        return False

def updateUserRoleText(userId, role):
    try:
        mycursor.execute(app_constants.SQL_UPDATE_USER_ROLE_TEXT, [role, int(userId)])
        mydb.commit()
        return True
    except Exception as e:
        trace(f"Error updating user role: {e}")
        return False

def updateUserDetails(userId, name, email, dob, role):
    trace(f"Attempting to update user details for ID {userId}")
    trace(f"New values - Name: '{name}', Email: '{email}', DOB: '{dob}', Role: '{role}'")
    
    try:
        # Check if name change is allowed (no duplicates)
        if name:
            mycursor.execute(app_constants.SQL_SELECT_USER_BY_NAME, [name])
            row = mycursor.fetchone()
            if row and int(row[0]) != int(userId):
                trace(f"Username '{name}' already exists for user ID {row[0]}")
                return False
        
        dob_value = dob if dob else None
        
        trace(f"Executing SQL: {app_constants.SQL_UPDATE_USER_DETAILS}")
        trace(f"With values: [{name}, {email}, {dob_value}, {role}, {userId}]")
        
        mycursor.execute(app_constants.SQL_UPDATE_USER_DETAILS, [name, email, dob_value, role, int(userId)])
        mydb.commit()
        
        # Verify the update was successful
        rows_affected = mycursor.rowcount
        trace(f"Rows affected: {rows_affected}")
        
        if rows_affected > 0:
            trace(f"Successfully updated user details for user ID: {userId}")
            
            # Verify the update by fetching the user
            mycursor.execute(app_constants.SQL_SELECT_USER_BY_ID, [userId])
            updated_user = mycursor.fetchone()
            trace(f"Verified updated user: {updated_user}")
            
            return True
        else:
            trace(f"No rows updated for user ID: {userId}")
            return False
            
    except Exception as e:
        trace(f"Error updating user details: {e}")
        trace(f"Error type: {type(e).__name__}")
        import traceback
        trace(f"Full traceback: {traceback.format_exc()}")
        mydb.rollback()  # Rollback in case of error
        return False