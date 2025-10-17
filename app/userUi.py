from flask import request, send_from_directory, redirect
from app.constants import CSS_STYLES
import app.user

try:
  from app.dbUtil import getDbInstance
  mydb = getDbInstance()
  mycursor = mydb.cursor()
except:
  print("Error occured while connecting DB")


def htmlBase(content, title="", sessionUUID=None , include_styles=False):
  if sessionUUID is None:
    menu = "<a href='/ui/login' class='btn'>Login</a>"
  else:
    menu = f"<a href='/ui/{sessionUUID}/user'>List of user</a>"
    menu += f" | <a href='/ui/{sessionUUID}/register' class='btn'>Register User</a>"
    menu += " | "
    menu += f"<a href='/ui/{sessionUUID}/logout'>Logout</a>"


  styles = ""
  if include_styles:
    styles = CSS_STYLES

  return f"""<!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {styles}
  </head>
  <body>
    <div class="bg-animation"></div>
    <div class="particles"></div>
    <div class="header">
      <a href="/" class="logo">ProteinDB</a>
      <div class="nav-menu" class="btn"> {menu} </div>
    </div>
    <div class="container">{content}</div>
  </body>
  </html>
  """


def showPleaseLogin():
   return htmlBase("""
   <div class="login-card">
        <div class="login-header">
        <h1 class="login-title">Alphafold</h1>
    
      </div>
    <form action="/ui/login" method="POST">
        <div class="form-group">
          <input type="text" id="userName" name="userName" class="form-input"  
                 placeholder=" " autocomplete="username">
          <label class="form-label" for="userName">User</label>
        </div>
        <div class="form-group">
          <input type="password" id="pass" name="pass" class="form-input"  
                 placeholder=" " autocomplete="current-password">
          <label class="form-label" for="pass">Password</label>
        </div>
        <button type="submit" class="login-btn">Login</button>
      </form></div>
     """, title="Please login", include_styles=True)


def showUserLoggedIn(sessionUUID):
   return htmlBase(f"""
    <div class="content-card">
      <div class="success-message">
        <h2>successfull</h2>
        <p>Welcome to the advanced protein research Alphafold</p>
      </div>
      <div style="text-align: center;">
        <a href="/ui/{sessionUUID}/user" class="action-link">
          Access Users
        </a>
      </div>
    </div>
    """, title="NEXUS Research Hub", sessionUUID=sessionUUID, include_styles=True)


def createEntrypoints(webapp):
  @webapp.get("/ui/<sessionUUID>/user")
  def entrypoint_ui_list_users(sessionUUID):
    deleted_user = request.args.get("deleted")
    notif = ""
    if deleted_user:
        notif = f"""
        <div class="success-message" style="margin-bottom: 1.5rem;">
            ✅ User <strong>{deleted_user}</strong> was successfully deleted.
        </div>
        """

    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
        return showPleaseLogin()

    html = '<div class="content-card">'
    html += notif
    html += '<h1 style="margin-bottom: 2rem; color: #00d4ff; font-size: 2rem; font-weight: 700;">🧬 List of Users</h1>'
    html += '<ul class="user-list">'

    for u in app.user.getListOfUsers():
      html += f"""
    <li class="user-card" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: #1e293b; border-radius: 8px; margin-bottom: 1rem;">
      <a href='/ui/{sessionUUID}/user/{u['id']}' class="user-link" style="color: #00d4ff; font-weight: 600; text-decoration: none;">
        {u['name']}
      </a>
      <form action="/ui/{sessionUUID}/user/{u['id']}/delete" method="POST" onsubmit="return confirm('Are you sure you want to delete user {u['name']}?');" style="margin-left: 1rem;">
        <button type="submit" style="background: none; border: none; color: #f87171; font-size: 1.25rem; cursor: pointer;">❌</button>
      </form>
    </li>
    """


    html += '</ul>'
    
    html += '</div>'
    
    return htmlBase(html, title="Research Network", sessionUUID=sessionUUID, include_styles=True)

  @webapp.post("/ui/<sessionUUID>/user/add")
  def entrypoint_ui_insert_user(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
      return showPleaseLogin()

    newUserName = request.form["name"]

    return htmlBase(
      '<div class="content-card"><div class="error-message">⚠️ User creation module is in quantum development phase.</div></div>', 
      title="Add Researcher", sessionUUID=sessionUUID, include_styles=True
    )


  @webapp.get("/ui/<sessionUUID>/user/<userIdText>")
  def entrypoint_ui_show_user(sessionUUID, userIdText):
    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
      return showPleaseLogin()

    userId = int(userIdText)
    if f"{userId}" != userIdText:

      return htmlBase(
      '<div class="content-card"><div class="error-message">⚠️ User creation module is in quantum development phase.</div></div>', 
      title="Add Researcher", sessionUUID=sessionUUID, include_styles=True
    )

    user = app.user.getUser(userId)
    if user is not None:
      html = '<div class="content-card">'
      html += f"<h1 style='color: #00d4ff; margin-bottom: 2rem; font-size: 2rem; font-weight: 700;'>👨‍🔬 {user[1]}</h1>"
      html += '<table class="user-table">'
      html += f"<tr><th>User ID</th><td>{user[0]}</td></tr>"
      html += f"<tr><th>User Name</th><td>{user[1]}</td></tr>"
      html += f"<tr><th>Admin User</th><td>{'True' if user[3] else'False'}</td></tr>"
      html += '</table>'
      html += '</div>'
      return htmlBase(html, title=f"Profile: {user[1]}", sessionUUID=sessionUUID, include_styles=True)
    else:
      return htmlBase(
        '<div class="content-card"><div class="error-message">❌ Researcher profile not found in quantum database.</div></div>', 
        title="Profile Access", sessionUUID=sessionUUID, include_styles=True
      )


  @webapp.post("/ui/<sessionUUID>/user/<userIdText>/delete")
  def entrypoint_ui_remove_user(sessionUUID, userIdText):
    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
      return showPleaseLogin()

    try:
        userId = int(userIdText)
        user = app.user.getUser(userId)
        
        if user and mycursor and mydb and (sessionUUID.split('-')[-1] != userIdText):
          app.user.deleteUser(userId)
          print(f"Successfully deleted user: {user[1]}")
          return redirect(f"/ui/{sessionUUID}/user?deleted={user[1]}")
        else:
          print("Deleting current self admin account is not allowed. Please contact IT department.")
            
    except Exception as e:
        print(f"Delete user error: {e}")

    return redirect(f"/ui/{sessionUUID}/user")

  @webapp.post("/ui/<sessionUUID>/user/<userIdText>")
  def entrypoint_ui_edit_user(sessionUUID, userIdText):
    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
      return showPleaseLogin()

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return htmlBase("<p>This item was not found.</p>", sessionUUID=sessionUUID)

    # TODO: Edit the user in database
    user = app.user.getUser(userId)
    newIsAdmin = request.form["isAdmin"]
    if user is not None:
      return htmlBase(f"<p>The user '{user['name']} was successfully changed.</p>", sessionUUID=sessionUUID)
    else:
      return htmlBase("<p>This item was not found.</p>", sessionUUID=sessionUUID)


  @webapp.get("/ui/login")
  def entrypoint_ui_login():
    return showPleaseLogin()

  @webapp.post("/ui/login")
  def entrypoint_ui_dologin():
    # TODO: actually log in
    sessionUUID = None
    if "userName" in request.form and "pass" in request.form:
      sessionUUID = app.user.doLogin(request.form["userName"], request.form["pass"] )

    if sessionUUID is not None and app.user.isLoggedIn(sessionUUID):
      return showUserLoggedIn(sessionUUID)
    else:
      return htmlBase("""<div class="login-card">LOGIN FAILED</div>""", 
                      title="Please login", include_styles=True)

  @webapp.get("/ui/<sessionUUID>/logout")
  def entrypoint_ui_logout(sessionUUID):
    app.user.doLogout(sessionUUID)

    return htmlBase('<div class="login-card"><div class="success-message"><h2> Alphafold Disconnected</h2><p>You have been safely logged out.</p></div><div style="text-align: center; margin-top: 2rem;"><a href="/ui/login" class="action-link">← Reconnect to Alphafold</a></div></div>', 
      title="Quantum Logout Complete", include_styles=True)


  @webapp.get("/favicon.ico")
  def entrypoint_ui_fav_ico():
    return send_from_directory('static', 'favicon.ico', mimetype='image/x-icon')

  @webapp.get("/ui/<sessionUUID>/register")
  def entrypoint_ui_register_form(sessionUUID):
    return htmlBase(f"""           

    <div class="login-card">
      <div class="login-header">
        <h1>Register New User</h1>
      </div>
      <form action='/ui/{sessionUUID}/register' method='POST'>
        <div class="form-group">
          <input type='text' name='userName' class="form-input" autocomplete="username" /> 
          <label class="form-label" for="userName">User</label>
        </div>
        <div class="form-group">
           <input type='password' name='password' class="form-input" autocomplete="username" />         
           <label class="form-label" for="pass">Password</label>
        </div>
        <div class="form-group">
          <input type='submit' value='Register' class="login-btn" />
        </div>       
      </form>
    </div>
    """, title="Register" , include_styles=True)

  @webapp.post("/ui/<sessionUUID>/register")
  def entrypoint_ui_register_user(sessionUUID):

    userName = request.form.get("userName")
    password = request.form.get("password")

    if not userName or not password:
        return htmlBase(f"""
        <div class="registration-result-card registration-error">
          <div class="registration-header">
            <h2>Registration</h2>
          </div>
          <div class="registration-status">
            <span class="status-icon error-icon">⚠️</span>
            <div class="error-message-text">
              <p class="status-message">Missing Information</p>
              <p class="status-details">Username and password are required to create an account.</p>
            </div>
          </div>
          <div class="registration-action">
            <a href='/ui/{sessionUUID}/register' class="action-btn error-action">Try Again</a>
          </div>
        </div>
        """, title="Registration Error", include_styles=True)

    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
      return showPleaseLogin()

    created = app.user.registerUser(userName, password)

    if created:
        return htmlBase(f"""
        <div class="registration-result-card registration-success">
          <div class="registration-header">
            <h2>Registration</h2>
          </div>
          <div class="registration-status">
            <span class="status-icon success-icon">✅</span>
            <div class="success-message-text">
              <p class="status-message">Account Created Successfully!</p>
              <p class="status-details">User <span class="username-highlight">{userName}</span> has been registered and is ready to access the AlphaFold system.</p>
            </div>
          </div>
          <div class="registration-action">
            <a href='/ui/login' class="action-btn success-action">Continue to Login</a>
          </div>
        </div>
        """, title="Registration Successful", include_styles=True)
    else:
        return htmlBase(f"""
        <div class="registration-result-card registration-error">
          <div class="registration-header">
            <h2>Registration</h2>
          </div>
          <div class="registration-status">
            <span class="status-icon error-icon">❌</span>
            <div class="error-message-text">
              <p class="status-message">Registration Failed</p>
              <p class="status-details">The username <span class="username-highlight">{userName}</span> may already exist or there was a system error.</p>
            </div>
          </div>
          <div class="registration-action">
            <a href='/ui/{sessionUUID}/register' class="action-btn error-action">Try Different Username</a>
          </div>
        </div>
        """, title="Registration Failed", include_styles=True)

