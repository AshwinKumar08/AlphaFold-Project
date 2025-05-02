from flask import request

import app.user

def htmlBase(content, title="", sessionUUID=None):
  if sessionUUID is None:
    menu = "<a href='/ui/login'>Login</a>"
  else:
    menu = f"<a href='/ui/{sessionUUID}/user'>List of user</a>"
    menu += " | "
    menu += f"<a href='/ui/{sessionUUID}/logout'>Logout</a>"

  return f"""<html><head><title>{title}</title></head>
  <body><div class="topmenu">{menu}</div>{content}</body>
  </html>
    """

def showPleaseLogin():
  return htmlBase("""
    <h1>Please login</h1>
    <form action="/ui/login" method="POST">
    <p><em>Username</em><input type="text" name="userName" /></p>
    <p><em>Password</em><input type="password" name="pass" /></p>
    <p><input type="submit" value="login" /></p>
    </form>
    """, title="Please login")

def showUserLoggedIn(sessionUUID):
  return htmlBase(f"""
    <p>You successfully logged in.</p>
    <p><a href="/ui/{sessionUUID}/user">Show list of user</a></p>
    """, sessionUUID=sessionUUID)


def createEntrypoints(webapp):
  @webapp.get("/ui/<sessionUUID>/user")
  def entrypoint_ui_list_users(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
      return showPleaseLogin()

    # TODO: Read users from database
    html = "<ul>"
    for u in app.user.getListOfUsers():
      html += f"<li><a href='/ui/{sessionUUID}/user/{u['id']}'>{u['name']}</a></li>"
    html += "</ul>"
    return htmlBase(html, sessionUUID=sessionUUID)

  @webapp.post("/ui/<sessionUUID>/user/add")
  def entrypoint_ui_insert_user(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
      return showPleaseLogin()

    newUserName = request.form["name"]
    # TODO: store the new user
    return htmlBase("<p>This action is not implemented jet.</p>", sessionUUID=sessionUUID)


  @webapp.get("/ui/<sessionUUID>/user/<userIdText>")
  def entrypoint_ui_show_user(sessionUUID, userIdText):
    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
      return showPleaseLogin()

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return htmlBase("<p>This item was not found.</p>", sessionUUID=sessionUUID)

    # TODO: Find user in database
    user = app.user.getUser(userId)
    if user is not None:
      html = f"<h1>User '{user['name']}'</h1>"
      html += "<table>"
      for k in user:
        html += f"<tr><th>{k}</th><td>{user[k]}</td><tr>"
      html += "</table>"
      return htmlBase(html, sessionUUID=sessionUUID)
    else:
      return htmlBase("<p>This item was not found.</p>", sessionUUID=sessionUUID)


  @webapp.post("/ui/<sessionUUID>/user/<userIdText>/delete")
  def entrypoint_ui_remove_user(sessionUUID, userIdText):
    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
      return showPleaseLogin()

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return htmlBase("<p>This item was not found.</p>", sessionUUID=sessionUUID)

    # TODO: Remove the user in database
    user = getUser(userId)
    if user is not None:
      return htmlBase(f"<p>The user '{user['name']} was successfully removed.</p>", sessionUUID=sessionUUID)
    else:
      return htmlBase("<p>This item was not found.</p>", sessionUUID=sessionUUID)


  @webapp.post("/ui/<sessionUUID>/user/<userIdText>")
  def entrypoint_ui_edit_user(sessionUUID, userIdText):
    if not app.user.isLoggedIn(sessionUUID) or not app.user.isAdmin(sessionUUID):
      return showPleaseLogin()

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return htmlBase("<p>This item was not found.</p>", sessionUUID=sessionUUID)

    # TODO: Edit the user in database
    user = getUser(userId)
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
    if "userName" in request.form:
      sessionUUID = app.user.doLogin(request.form["userName"])

    if sessionUUID is not None and app.user.isLoggedIn(sessionUUID):
      return showUserLoggedIn(sessionUUID)
    else:
      return htmlBase("<p>Failed to login.</p>")



  @webapp.get("/ui/<sessionUUID>/logout")
  def entrypoint_ui_logout(sessionUUID):
    app.user.doLogout(sessionUUID)
    # TODO: actually log out
    return htmlBase("<p>You successfully logged out.</p>")


