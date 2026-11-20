from flask import request, send_from_directory, redirect
from app.constants import CSS_STYLES , JS_SCRIPTS
import app.user
import app.stats 
import sys
import app.constants as app_constants


try:
  from app.dbUtil import getDbInstance
  mydb = getDbInstance()
  mycursor = mydb.cursor()
except:
  print("Error occured while connecting DB")


def htmlBase(content, title="", sessionUUID=None, include_styles=False):
  if sessionUUID is None:
        menu = """
        <a href='/ui/login' class='btn btn-primary'>🔐 Login</a>
        """
        logo_link = "/"
  else:
        current_user = app.user.getUserFromSession(sessionUUID)
        unread = app.user.getUnreadCount(current_user["id"]) if current_user else 0
        unread_badge = (
            f"<span class='badge'>{unread}</span>"
            if unread > 0 else ""
        )
        menu = f"""
        <a href='/ui/{sessionUUID}/home' class='btn'>🏠 Home</a>
        <a href='/ui/{sessionUUID}/messages' class='btn'>
            💬 Messages{ unread_badge}
        </a>
        <a href='/ui/{sessionUUID}/support' class='btn'>🎫 Support</a>
        <a href='/ui/{sessionUUID}/profile' class='btn'>👤 My Profile</a>
        """
        if app.user.isAdmin(sessionUUID):
            menu += f"""
            <span class='admin-section'>
                <a href='/ui/{sessionUUID}/user' class='btn admin-btn'> Manage Users</a>
                <a href='/ui/{sessionUUID}/register' class='btn admin-btn'> Register User</a>
            </span>
            """
        menu += " | "
        menu += f"<a href='/ui/{sessionUUID}/tasks'>Task Management</a>"
        menu += " | "
        menu += f"""
        <a href='/ui/{sessionUUID}/logout' class='btn logout-btn'>🚪 Logout</a>
        """
        logo_link = f"/ui/{sessionUUID}/home"
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
      <a href="{logo_link}" class="logo">Alphafold</a>
      <div class="nav-menu" class="btn"> {menu} </div>
    </div>
    <div class="container">{content}</div>
    {JS_SCRIPTS}
  </body>
  </html>
  """


def showPleaseLogin(error_message="",  remaining_seconds=None):
    """
    Renders the login page with a lockout timer if remaining_seconds is provided.
    """
    print("="*60)
    print("showPleaseLogin called")
    print(f"error_message: {error_message}")
    print(f"remaining_seconds: {remaining_seconds}")
    print("="*60)
    

    error_html = ""
    if error_message:
        error_html = f"""
        <div class="error-message" style="margin-bottom: 1.5rem;">
            ❌ {error_message}
        </div>
        """
    # Get timer value
    timer_value = 0
    if remaining_seconds is not None:
        try:
            timer_value = int(remaining_seconds)
        except:
            timer_value = 0
    
    # Only show timer div if there's a lockout
    timer_html = ""
    if timer_value > 0:
        timer_html = f"""
        <div id="lockout-timer" style="color: #ff6b6b; font-weight: bold; margin-bottom: 20px; text-align: center; font-size: 1.2rem; background: rgba(255, 107, 107, 0.1); border: 1px solid #ff6b6b; padding: 15px; border-radius: 8px;">
            ⏳ Loading timer...
        </div>
        """

    
    return htmlBase(f"""
    <div class="login-card">
        <div class="login-header">
            <h1 class="login-title">AlphaFold</h1>
        </div>
    
        {error_html}
        
        {timer_html}

        <form action="/ui/login" method="POST" id="loginForm">
            <div class="form-group">
                <label for="userName" style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;">Username</label>
                <input type="text" id="userName" name="userName" class="form-input" autocomplete="username" required />
            </div>
            
            <div class="form-group">
                <label for="pass" style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;">Password</label>
                <div style="position: relative;">
                    <input type="password" id="pass" name="pass" class="form-input" autocomplete="current-password" required 
                           style="padding-right: 3rem;">
                    <button type="button" id="togglePassword" 
                            onclick="togglePasswordVisibility('pass', 'togglePassword')"
                            style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); 
                                   background: none; border: none; color: rgba(255,255,255,0.6); 
                                   cursor: pointer; font-size: 1.2rem; padding: 0.25rem;">
                        👁️
                    </button>
                </div>
            </div>
            
            <button type="submit" class="login-btn" style="margin-top: 1rem;">Login</button>
        </form>
        
        <div style="text-align: center; margin-top: 2rem; color: rgba(255,255,255,0.6); font-size: 0.9rem;">
            Need an account? Contact an administrator for access.
        </div>
        
        <script>
        function togglePasswordVisibility(inputId, buttonId) {{
            const passwordInput = document.getElementById(inputId);
            const toggleButton = document.getElementById(buttonId);
            
            if (passwordInput.type === 'password') {{
                passwordInput.type = 'text';
                toggleButton.innerHTML = '🙈';
                toggleButton.title = 'Hide password';
            }} else {{
                passwordInput.type = 'password';
                toggleButton.innerHTML = '👁️';
                toggleButton.title = 'Show password';
            }}
        }}

        // Lockout timer
        var TIMER_SECONDS = {timer_value};
        
        if (TIMER_SECONDS > 0) {{
            var remaining = TIMER_SECONDS;
            var timerEl = document.getElementById("lockout-timer");
            var btn = document.getElementById("login-btn");
            var inputs = document.querySelectorAll(".form-input");
            
            if (timerEl && btn) {{
                // Disable form
                btn.disabled = true;
                btn.innerText = "🔒 Account Locked";
                btn.style.opacity = "0.5";
                btn.style.cursor = "not-allowed";
                
                for (var i = 0; i < inputs.length; i++) {{
                    inputs[i].disabled = true;
                }}
                
                function updateTimer() {{
                    var minutes = Math.floor(remaining / 60);
                    var seconds = remaining % 60;
                    var display = String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
                    timerEl.innerHTML = "⏳ Please wait " + display;
                }}
                
                updateTimer();
                
                var countdown = setInterval(function() {{
                    remaining--;
                    
                    if (remaining <= 0) {{
                        clearInterval(countdown);
                        
                        // Re-enable form
                        for (var i = 0; i < inputs.length; i++) {{
                            inputs[i].disabled = false;
                        }}
                        btn.disabled = false;
                        btn.innerText = "Login";
                        btn.style.opacity = "1";
                        btn.style.cursor = "pointer";
                        
                        timerEl.innerHTML = "✅ You can try again now";
                        setTimeout(function() {{
                            timerEl.style.display = "none";
                        }}, 3000);
                        return;
                    }}
                    
                    updateTimer();
                }}, 1000);
            }}
        }}
        document.getElementById('loginForm').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                this.submit();
            }}
        }});
        </script>
    </div>
    """, title="Login to AlphaFold", include_styles=True)


def showUserLoggedIn(sessionUUID):
   return redirect(f"/ui/{sessionUUID}/home")


# Homepage UI
def showHomepage(sessionUUID, user_name, error_message=""):    
    html = f"""
    <div class="content-card">
        <div style="text-align: center; margin-bottom: 2.5rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🔬</div>
            <h1 style="color: #00d4ff; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;">
                Welcome, {user_name}!
            </h1>
        </div>
        
        <div style="background: rgba(76, 205, 196, 0.1); border: 1px solid rgba(76, 205, 196, 0.3); border-radius: 16px; padding: 2rem; margin-bottom: 2.5rem;">
            <h2 style="color: #4ecdc4; font-size: 1.8rem; font-weight: 700; margin-bottom: 1rem;">
                AlphaFold DB
            </h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; line-height: 1.7; margin-bottom: 1.5rem;">
                AlphaFold provides open access to over 200 million protein structure predictions to accelerate scientific research.
            </p>
            <div style="display: flex; align-items: center; gap: 0.75rem; color: rgba(255,255,255,0.8); font-size: 0.95rem;">
                <span style="font-size: 1.2rem;">🔗</span>
                <span>For more information, refer: </span>
                <a href="https://alphafold.com/" target="_blank" style="color: #00d4ff; text-decoration: none; font-weight: 600;">
                    https://alphafold.com/
                </a>
            </div>
        </div>
    </div>
    """
    
    return htmlBase(html, title="AlphaFold Home", sessionUUID=sessionUUID, include_styles=True)


#  User profile
def showUserProfile(sessionUUID, user_data, message_type="", message_text=""):
    message_html = ""
    if message_type == "success":
        message_html = f"""
        <div class="success-message" style="margin-bottom: 1.5rem;">
            ✅ {message_text}
        </div>
        """
    elif message_type == "error":
        message_html = f"""
        <div class="error-message" style="margin-bottom: 1.5rem;">
            ❌ {message_text}
        </div>
        """
    
    # Check if user is admin
    is_admin = user_data[3] == 1 if len(user_data) > 3 else False
    email_display = user_data[5] if len(user_data) > 5 and user_data[5] else "Not set"
    dob_display = user_data[6] if len(user_data) > 6 and user_data[6] else "Not set"
    role_display = user_data[7] if len(user_data) > 7 and user_data[7] else "Not set"

    last_login_display = "Never"
    if len(user_data) > 8 and user_data[8]:
        try:
            if isinstance(user_data[8], str):
                last_login_display = user_data[8]
            else:
                last_login_display = user_data[8].strftime("%B %d, %Y at %I:%M %p")
        except:
            last_login_display = str(user_data[8])

    
    if dob_display and dob_display != "Not set":
        try:
            parts = dob_display.split("-")
            if len(parts) == 3:
                dob_display = f"{parts[2]}-{parts[1]}-{parts[0]}"
        except:
            pass 
    
    html = f"""
    <div class="content-card">
        <div style="display: flex; align-items: center; margin-bottom: 2rem;">
            <h1 style="color: #00d4ff; font-size: 2rem; font-weight: 700;">👤 My Profile</h1>
        </div>
        
        {message_html}
        
        <!-- User ID & Username Box -->
        <div style="background: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">User ID</div>
                    <div style="color: white; font-size: 1.2rem; font-weight: 700;">{user_data[0]}</div>
                </div>
                <div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">Username</div>
                    <div style="color: white; font-size: 1.2rem; font-weight: 700;">{user_data[1]}</div>
                </div>
            </div>
        </div>
        
        <!-- Personal Information Box -->
        <div style="background: rgba(76, 205, 196, 0.05); border: 1px solid rgba(76, 205, 196, 0.2); border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
            <h2 style="color: #4ecdc4; font-size: 1.3rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem;"></span> Personal Information
            </h2>
            <table class="user-table" style="width: 100%; border-collapse: collapse; background: transparent;">
                <tbody>
                    <tr>
                        <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.7); font-weight: 600; width: 30%;">Email Address</td>
                        <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: white; font-weight: 600;">{email_display}</td>
                    </tr>
                    <tr>
                        <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.7); font-weight: 600;">Date of Birth</td>
                        <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: white; font-weight: 600;">{dob_display}</td>
                    </tr>
                    <tr>
                        <td style="padding: 1rem; color: rgba(255,255,255,0.7); font-weight: 600;">Role</td>
                        <td style="padding: 1rem; color: white; font-weight: 600;">{role_display}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- Account Information Box -->
        <div style="background: rgba(255, 107, 107, 0.05); border: 1px solid rgba(255, 107, 107, 0.2); border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
            <h2 style="color: #ff6b6b; font-size: 1.3rem; font-weight: 700; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem;"></span> Account Information
            </h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
                <div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">Account Type</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600;">
                        <span style="color: {'#00d4ff' if is_admin else '#4ecdc4'};">
                            {' Administrator' if is_admin else ' Regular User'}
                        </span>
                    </div>
                </div>
                <div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">Account Status</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600;">
                        <span style="color: {'#4ecdc4' if user_data[4] == 1 else '#ff6b6b'};">
                            {' Enabled' if user_data[4] == 1 else ' Disabled'}
                        </span>
                    </div>
                </div>
                <div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">Last Login</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600;">
                        <span style="color: #4ecdc4;">
                            🕐 {last_login_display}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        
        <div style="display: flex; gap: 1rem; margin-top: 2rem;">
            <a href='/ui/{sessionUUID}/home' 
               style="display: inline-flex; 
                      align-items: center; 
                      gap: 0.5rem; 
                      padding: 0.75rem 1.5rem; 
                      background: rgba(255, 255, 255, 0.1); 
                      border: 1px solid rgba(255, 255, 255, 0.2); 
                      border-radius: 12px; 
                      color: #00d4ff; 
                      text-decoration: none; 
                      font-weight: 600;
                      font-size: 0.95rem;">
                ← Back to Home
            </a>
            <a href='/ui/{sessionUUID}/profile/edit' 
               style="display: inline-flex; 
                      align-items: center; 
                      gap: 0.5rem; 
                      padding: 0.75rem 1.5rem; 
                      background: #00d4ff; 
                      border: 1px solid #00d4ff; 
                      border-radius: 12px; 
                      color: #0a0a0a; 
                      text-decoration: none; 
                      font-weight: 700;
                      font-size: 0.95rem;">
                ✏️ Edit Profile
            </a>
        </div>
        
        <!-- Admin section for editing other users -->
        {f'''
        <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
            <h3 style="color: #ff6b6b; margin-bottom: 1rem; font-size: 1.2rem; font-weight: 600;">⚠️ Administrator Controls</h3>
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 1rem; font-size: 0.9rem;">
                As an administrator, you can manage other users.
            </p>
            <a href='/ui/{sessionUUID}/user' class='action-link'>
                👥 Go to User Management
            </a>
        </div>
        ''' if is_admin else ""}
    </div>
    """
    return htmlBase(html, title="My Profile", sessionUUID=sessionUUID, include_styles=True)


def showEditProfile(sessionUUID, user_data, error_message=""):
    error_html = ""
    if error_message:
        error_html = f"""
        <div class="error-message" style="margin-bottom: 1.5rem;">
            ❌ {error_message}
        </div>
        """
    email_value = user_data[5] if len(user_data) > 5 else ""
    dob_value = user_data[6] if len(user_data) > 6 else ""
    role_value = user_data[7] if len(user_data) > 7 else ""
    
    dob_display = ""
    if dob_value:
        try:
            parts = dob_value.split("-")
            if len(parts) == 3:
                dob_display = f"{parts[2]}-{parts[1]}-{parts[0]}"
            else:
                dob_display = dob_value
        except:
            dob_display = dob_value
    
    html = f"""
    <div class="content-card">
        <div style="display: flex; align-items: center; margin-bottom: 2rem;">
            <a href='/ui/{sessionUUID}/profile' style="color: #00d4ff; text-decoration: none; margin-right: 1rem; font-size: 1.5rem;">←</a>
            <h1 style="color: #00d4ff; font-size: 2rem; font-weight: 700;">✏️ Edit Profile</h1>
        </div>
        
        {error_html}
        
        <!-- Edit User Details Form -->
        <form action='/ui/{sessionUUID}/profile/edit-details' method='POST' id="editDetailsForm">
            <h3 style="color: #00d4ff; margin-bottom: 1rem; font-size: 1.2rem; font-weight: 600;">Edit Personal Information</h3>
            
            <div class='form-group'>
                <label for='edit_name' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>Username</label>
                <input type='text' id='edit_name' name='edit_name' class='form-input' value='{user_data[1]}' required />
                <small style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">Enter new username or keep current</small>
            </div>
            
            <div class='form-group'>
                <label for='edit_email' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>Email Address</label>
                <input type='email' id='edit_email' name='edit_email' class='form-input' value='{email_value}' />
                <small style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">Optional</small>
            </div>
            
            <div class='form-group'>
                <label for='edit_dob' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>Date of Birth</label>
                <input type='text' id='edit_dob' name='edit_dob' class='form-input' value='{dob_display}' placeholder='DD-MM-YYYY' />
                <small style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">Optional - Format: DD-MM-YYYY</small>
            </div>
            
            <div class='form-group'>
                <label for='edit_role' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>Role</label>
                <input type='text' id='edit_role' name='edit_role' class='form-input' value='{role_value}' placeholder='e.g., Researcher, Student, Professor' />
                <small style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">Optional - Your position or role</small>
            </div>
            
            <button type='submit' class='login-btn' style='margin-top: 1rem; width: 100%;'>Save Profile Changes</button>
        </form>
        
        <!-- Password Change Section -->
        <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
            <h3 style="color: #00d4ff; margin-bottom: 1rem; font-size: 1.2rem; font-weight: 600;">Change Password</h3>
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 1.5rem; font-size: 0.9rem;">
                Need to update your password? Click the button below to go to the password change page.
            </p>
            <a href='/ui/{sessionUUID}/profile/change-password' 
               style="display: inline-flex; 
                      align-items: center; 
                      gap: 0.5rem; 
                      padding: 0.75rem 1.5rem; 
                      background: #ff6b6b; 
                      border: 1px solid #ff6b6b; 
                      border-radius: 12px; 
                      color: white; 
                      text-decoration: none; 
                      font-weight: 700;
                      font-size: 0.95rem;">
                🔐 Change Password
            </a>
        </div>
        
        <div style="display: flex; gap: 1rem; margin-top: 2rem;">
            <a href='/ui/{sessionUUID}/profile' 
               style="display: inline-flex; 
                      align-items: center; 
                      gap: 0.5rem; 
                      padding: 0.75rem 1.5rem; 
                      background: rgba(255, 255, 255, 0.1); 
                      border: 1px solid rgba(255, 255, 255, 0.2); 
                      border-radius: 12px; 
                      color: #00d4ff; 
                      text-decoration: none; 
                      font-weight: 600;
                      font-size: 0.95rem;">
                ← Back to Profile
            </a>
        </div>
        
        <script>

        // Enter Key is accapted to submit form
        document.getElementById('editDetailsForm')?.addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                this.submit();
            }}
        }});
        </script>
    </div>
    """
    return htmlBase(html, title="Edit Profile", sessionUUID=sessionUUID, include_styles=True)


def showChangePassword(sessionUUID, user_data, error_message="", success_message=""):
    error_html = ""
    if error_message:
        error_html = f"""
        <div class="error-message" style="margin-bottom: 1.5rem;">
            ❌ {error_message}
        </div>
        """
    
    success_html = ""
    if success_message:
        success_html = f"""
        <div class="success-message" style="margin-bottom: 1.5rem;">
            ✅ {success_message}
        </div>
        """
    
    html = f"""
    <div class="content-card">
        <div style="display: flex; align-items: center; margin-bottom: 2rem;">
            <a href='/ui/{sessionUUID}/profile/edit' style="color: #00d4ff; text-decoration: none; margin-right: 1rem; font-size: 1.5rem;">←</a>
            <h1 style="color: #00d4ff; font-size: 2rem; font-weight: 700;">🔐 Change Password</h1>
        </div>
        
        {success_html}
        {error_html}
        
        <form action='/ui/{sessionUUID}/profile/change-password' method='POST' id="passwordForm">
            <div class='form-group'>
                <label for='current_password' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>Current Password</label>
                <div style="position: relative;">
                    <input type='password' id='current_password' name='current_password' class='form-input' required 
                           style="padding-right: 3rem;">
                    <button type="button" class="toggle-password-btn" 
                            onclick="togglePasswordVisibility('current_password', 'toggleCurrent')"
                            style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); 
                                   background: none; border: none; color: rgba(255,255,255,0.6); 
                                   cursor: pointer; font-size: 1.2rem; padding: 0.25rem;" 
                            id="toggleCurrent">
                        👁️
                    </button>
                </div>
            </div>
            
            <div class='form-group'>
                <label for='new_password' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>New Password</label>
                <div style="position: relative;">
                    <input type='password' id='new_password' name='new_password' class='form-input' required 
                           style="padding-right: 3rem;">
                    <button type="button" class="toggle-password-btn" 
                            onclick="togglePasswordVisibility('new_password', 'toggleNew')"
                            style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); 
                                   background: none; border: none; color: rgba(255,255,255,0.6); 
                                   cursor: pointer; font-size: 1.2rem; padding: 0.25rem;" 
                            id="toggleNew">
                        👁️
                    </button>
                </div>
            </div>
            
            <div class='form-group'>
                <label for='confirm_password' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>Confirm New Password</label>
                <div style="position: relative;">
                    <input type='password' id='confirm_password' name='confirm_password' class='form-input' required 
                           style="padding-right: 3rem;">
                    <button type="button" class="toggle-password-btn" 
                            onclick="togglePasswordVisibility('confirm_password', 'toggleConfirm')"
                            style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); 
                                   background: none; border: none; color: rgba(255,255,255,0.6); 
                                   cursor: pointer; font-size: 1.2rem; padding: 0.25rem;" 
                            id="toggleConfirm">
                        👁️
                    </button>
                </div>
            </div>
            
            <div style="display: flex; gap: 1rem; margin-top: 2rem;">
                <a href='/ui/{sessionUUID}/profile/edit' 
                   style="display: inline-flex; 
                          align-items: center; 
                          gap: 0.5rem; 
                          padding: 0.75rem 1.5rem; 
                          background: rgba(255, 255, 255, 0.1); 
                          border: 1px solid rgba(255, 255, 255, 0.2); 
                          border-radius: 12px; 
                          color: #00d4ff; 
                          text-decoration: none; 
                          font-weight: 600;
                          font-size: 0.95rem;">
                    ← Cancel
                </a>
                <button type='submit' class='login-btn' style='flex: 1;'>Change Password</button>
            </div>
        </form>
        
        <script>
        function togglePasswordVisibility(inputId, buttonId) {{
            const passwordInput = document.getElementById(inputId);
            const toggleButton = document.getElementById(buttonId);
            
            if (passwordInput.type === 'password') {{
                passwordInput.type = 'text';
                toggleButton.innerHTML = '🙈';
                toggleButton.title = 'Hide password';
            }} else {{
                passwordInput.type = 'password';
                toggleButton.innerHTML = '👁️';
                toggleButton.title = 'Show password';
            }}
        }}
        
        document.getElementById('passwordForm')?.addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                this.submit();
            }}
        }});
        </script>
    </div>
    """
    return htmlBase(html, title="Change Password", sessionUUID=sessionUUID, include_styles=True)


def check_admin_access(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    if not app.user.isAdmin(sessionUUID):
        return htmlBase("""
        <div class="content-card">
          <div class="error-message">
            <h2>⚠️ Administrator Access Required</h2>
            <p>Only administrators can perform this action.</p>
            <p>Please contact an administrator if you need to enable/disable users or modify user roles.</p>
            <p><a href="/" class="action-link">Return to Home</a></p>
          </div>
        </div>
        """, title="Admin Access Required", include_styles=True)
    
    return None  # User is admin, return None to proceed

# Replace the showMessages function in userUi.py (around line 450)

def showMessages(sessionUUID, user_id):
    messages = app.user.getUserMessages(user_id)
    unread_count = app.user.getUnreadCount(user_id)
    
    html = f"""
    <div class="content-card">
        <h1 style="color: #00d4ff; margin-bottom: 2rem;">💬 Messages 
            <span style="background: #ff6b6b; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem;">
                {unread_count} unread
            </span>
        </h1>
        
        <a href='/ui/{sessionUUID}/messages/compose' class='action-link' style='margin-bottom: 2rem; display: inline-block;'>
            ✉️ Compose New Message
        </a>
        
        <div style='margin-top: 2rem;'>
    """
    
    if messages and len(messages) > 0:
        for msg in messages:
            # Safely access message fields with defaults
            msg_id = msg[0] if len(msg) > 0 else 0
            sender_name = msg[2] if len(msg) > 2 else "Unknown"
            subject = msg[3] if len(msg) > 3 else "(No subject)"
            message_text = msg[4] if len(msg) > 4 else ""
            is_read = msg[6] if len(msg) > 6 else False
            created_at = msg[7] if len(msg) > 7 else ""
            
            read_status = "✅ Read" if is_read else "📬 Unread"
            read_color = "#4ecdc4" if is_read else "#ff6b6b"
            font_weight = "normal" if is_read else "font-weight: 700;"
            
            # Truncate message preview
            message_preview = message_text[:100] + "..." if len(message_text) > 100 else message_text
            
            html += f"""
            <div style='background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; 
                        border-left: 4px solid {read_color}; position: relative;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                    <div style='flex: 1;'>
                        <span style='color: #00d4ff; {font_weight}'>From: {sender_name}</span>
                        <span style='background: {read_color}; color: white; padding: 0.2rem 0.6rem; 
                                     border-radius: 12px; font-size: 0.75rem; margin-left: 1rem;'>
                            {read_status}
                        </span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 0.5rem;'>
                        <span style='color: rgba(255,255,255,0.6); font-size: 0.9rem;'>{created_at}</span>
                        <form action='/ui/{sessionUUID}/messages/{msg_id}/delete' method='POST' 
                              onsubmit="return confirm('Are you sure you want to delete this message?');" 
                              style='margin: 0;'>
                            <button type='submit' 
                                    style='background: none; border: none; color: #ff6b6b; 
                                           font-size: 1.2rem; cursor: pointer; padding: 0.25rem;
                                           transition: transform 0.2s ease;'
                                    onmouseover='this.style.transform="scale(1.2)"'
                                    onmouseout='this.style.transform="scale(1)"'>
                                🗑️
                            </button>
                        </form>
                    </div>
                </div>
                <div style='color: white; {font_weight} font-size: 1.1rem; margin-bottom: 0.5rem;'>
                    {subject}
                </div>
                <div style='color: rgba(255,255,255,0.8);'>{message_preview}</div>
                <div style='display: flex; gap: 1rem; margin-top: 1rem;'>
                    <a href='/ui/{sessionUUID}/messages/{msg_id}' 
                       style='color: #4ecdc4; text-decoration: none; font-weight: 600;'>
                        📖 Read more →
                    </a>
                    <a href='/ui/{sessionUUID}/messages/{msg_id}/toggle-read' 
                       style='color: #00d4ff; text-decoration: none; font-weight: 600;'>
                        {'Mark as Unread' if is_read else 'Mark as Read'}
                    </a>
                </div>
            </div>
            """
    else:
        html += "<div class='error-message'>No messages yet.</div>"
    
    html += "</div></div>"
    return htmlBase(html, title="Messages", sessionUUID=sessionUUID, include_styles=True)

def showComposeMessage(sessionUUID):
    users = app.user.getListOfUsers()
    
    html = f"""
    <div class="content-card">
        <h1 style="color: #00d4ff; margin-bottom: 2rem;">✉️ Compose Message</h1>
        
        <form method="POST" action="/ui/{sessionUUID}/messages/send">
            <div class="form-group">
                <label style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9);">Recipient</label>
                <select name="recipient_id" class="form-input" required>
                    <option value="">Select recipient...</option>
                    {''.join([f"<option value='{u['id']}'>{u['name']}</option>" for u in users])}
                </select>
            </div>
            
            <div class="form-group">
                <label style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9);">Subject</label>
                <input type="text" name="subject" class="form-input" required />
            </div>
            
            <div class="form-group">
                <label style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9);">Message</label>
                <textarea name="message" class="form-input" rows="8" required style="resize: vertical;"></textarea>
            </div>
            
            <div style="display: flex; gap: 1rem; margin-top: 2rem;">
                <a href='/ui/{sessionUUID}/messages' class='btn' style='background: rgba(255,255,255,0.1);'>Cancel</a>
                <button type="submit" class="login-btn" style="flex: 1;">Send Message</button>
            </div>
        </form>
    </div>
    """
    return htmlBase(html, title="Compose Message", sessionUUID=sessionUUID, include_styles=True)


def showSupportTickets(sessionUUID, user_id, is_admin):
    print(f"DEBUG: Loading support tickets - User ID: {user_id}, Is Admin: {is_admin}")
    
    # Everyone sees all tickets
    tickets = app.user.getUserTickets(user_id)
    
    print(f"DEBUG: Retrieved {len(tickets)} tickets")
    print(f"DEBUG: Tickets data: {tickets}")
    
    html = f"""
    <div class="content-card">
        <h1 style="color: #00d4ff; margin-bottom: 2rem;">🎫 Support Tickets</h1>
        
        <a href='/ui/{sessionUUID}/support/new' class='action-link' style='margin-bottom: 2rem; display: inline-block;'>
            ➕ Create New Ticket
        </a>
        
        <div style='margin-top: 2rem;'>
    """
    
    for ticket in tickets:
        status_colors = {'open': '#ff6b6b', 'in_progress': '#ffa500', 'closed': '#4ecdc4'}
        
        # Get ticket data
        ticket_id = ticket.get('id', 'N/A')
        subject = ticket.get('subject', 'No Subject')
        description = ticket.get('description', 'No description')
        status = ticket.get('status', 'open')
        priority = ticket.get('priority', 'medium')
        created_at = str(ticket.get('created_at', 'Unknown'))
        user_name = ticket.get('user_name', 'Unknown User')
        ticket_user_id = ticket.get('user_id', 0)
        
        # Show who created it
        creator_info = f"by {user_name}" if ticket_user_id != user_id else "by You"
        
        html += f"""
        <div style='background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border-left: 4px solid {status_colors.get(status, "#gray")};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h3 style='color: white; margin: 0;'>
                        <span style='color: #00d4ff; margin-right: 0.5rem;'>#{ticket_id}</span>
                        {subject}
                    </h3>
                    <span style='color: #4ecdc4; font-size: 0.9rem; margin-top: 0.25rem; display: inline-block;'>{creator_info}</span>
                </div>
                <span style='background: {status_colors.get(status, "#gray")}; padding: 0.3rem 1rem; border-radius: 20px; font-size: 0.85rem; white-space: nowrap;'>
                    {status.upper().replace('_', ' ')}
                </span>
            </div>
            <p style='color: rgba(255,255,255,0.8); margin-top: 1rem;'>{description[:150]}{"..." if len(str(description)) > 150 else ""}</p>
            <div style='color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-top: 0.5rem;'>
                Priority: <span style='color: {"#ff6b6b" if priority == "high" else "#ffa500" if priority == "medium" else "#4ecdc4"};'>{priority.upper()}</span> | Created: {created_at}
            </div>
        </div>
        """
    
    if not tickets:
        html += "<div class='error-message'>No support tickets yet. Create your first ticket above!</div>"
    
    html += "</div></div>"
    return htmlBase(html, title="Support Tickets", sessionUUID=sessionUUID, include_styles=True)


def showNewSupportTicket(sessionUUID):
    html = f"""
    <div class="content-card">
        <h1 style="color: #00d4ff; margin-bottom: 2rem;">➕ Create Support Ticket</h1>
        
        <form method="POST" action="/ui/{sessionUUID}/support/new">
            <div class="form-group">
                <label style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9);">Subject</label>
                <input type="text" name="subject" class="form-input" required />
            </div>
            
            <div class="form-group">
                <label style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9);">Priority</label>
                <select name="priority" class="form-input">
                    <option value="low">Low</option>
                    <option value="medium" selected>Medium</option>
                    <option value="high">High</option>
                </select>
            </div>
            
            <div class="form-group">
                <label style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9);">Description</label>
                <textarea name="description" class="form-input" rows="8" required style="resize: vertical;"></textarea>
            </div>
            
            <div style="display: flex; gap: 1rem; margin-top: 2rem;">
                <a href='/ui/{sessionUUID}/support' class='btn' style='background: rgba(255,255,255,0.1);'>Cancel</a>
                <button type="submit" class="login-btn" style="flex: 1;">Create Ticket</button>
            </div>
        </form>
    </div>
    """
    return htmlBase(html, title="New Support Ticket", sessionUUID=sessionUUID, include_styles=True)

#Entry points start here
def createEntrypoints(webapp):
  @webapp.get("/ui/<sessionUUID>/user")
  def entrypoint_ui_list_users(sessionUUID):
    admin_check = check_admin_access(sessionUUID)
    if admin_check:
        return admin_check

    deleted_user = request.args.get("deleted")
    search_query = request.args.get("search", "").strip()
    notif = ""
    if deleted_user:
        notif = f"""
        <div class="success-message" style="margin-bottom: 1.5rem;">
            ✅ User <strong>{deleted_user}</strong> was successfully deleted.
        </div>
        """
    search_query = request.args.get("search", "").strip()  
    role_filter = request.args.get("role", "")
    status_filter = request.args.get("status", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    filtered_users = app.user.getListOfUsers(search_query, role_filter, status_filter, date_from, date_to)
    has_active_filters = any([search_query, role_filter, status_filter, date_from, date_to])
    
    html = '<div class="content-card">'
    html += notif
    html += '<h1 style="margin-bottom: 2rem; color: #00d4ff; font-size: 2rem; font-weight: 700;">🧬 List of Users</h1>'
    
    # Search form
    html += f"""
    <form method="GET" action="/ui/{sessionUUID}/user" style="margin-bottom: 2rem;">
    
      <!-- Search Field -->
      <div class="form-group" style="position: relative;">
        <input type="text" 
               name="search" 
               class="form-input" 
               placeholder="Search users by name..." 
               value="{search_query}"
               style="padding-right: 3rem;">
        <button type="submit" 
                style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); background: none; border: none; color: #00d4ff; cursor: pointer;">
          🔍
        </button>
      </div>
      
      <!-- Filter Section -->
      <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 1.5rem; margin-top: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <h3 style="color: #4ecdc4; font-size: 1.1rem; font-weight: 600; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
            🎯 Advanced Filters
          </h3>
          
          <!-- Filter Buttons - Top Right -->
          <div style="display: flex; gap: 1rem;">
            <button type="submit" 
                    style="padding: 0.75rem 1.5rem; 
                           background: linear-gradient(135deg, #4ecdc4, #44a08d); 
                           color: white; 
                           border: none; 
                           border-radius: 12px; 
                           font-weight: 600; 
                           cursor: pointer; 
                           transition: all 0.3s ease;">
              Apply Filters
            </button>
            <a href="/ui/{sessionUUID}/user" 
               style="padding: 0.75rem 1.5rem; 
                      background: rgba(255, 255, 255, 0.1); 
                      color: #00d4ff; 
                      border: 1px solid rgba(255, 255, 255, 0.2); 
                      border-radius: 12px; 
                      font-weight: 600; 
                      text-decoration: none; 
                      display: inline-flex; 
                      align-items: center; 
                      transition: all 0.3s ease;">
              Clear All Filters
            </a>
          </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
          <!-- Role Filter -->
          <div>
            <label style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.8); font-weight: 500; font-size: 0.9rem;">👤 Role</label>
            <select name="role" class="form-input" style="width: 100%; padding: 0.75rem;">
              <option value="">All Roles</option>
              <option value="admin" {'selected' if role_filter == 'admin' else ''}>Administrator</option>
              <option value="regular" {'selected' if role_filter == 'regular' else ''}>Regular User</option>
            </select>
          </div>
          
          <!-- Status Filter -->
          <div>
            <label style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.8); font-weight: 500; font-size: 0.9rem;">✅ Status</label>
            <select name="status" class="form-input" style="width: 100%; padding: 0.75rem;">
              <option value="">All Status</option>
              <option value="enabled" {'selected' if status_filter == 'enabled' else ''}>Enabled</option>
              <option value="disabled" {'selected' if status_filter == 'disabled' else ''}>Disabled</option>
            </select>
          </div>
          
          <!-- Date From -->
          <div>
            <label style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.8); font-weight: 500; font-size: 0.9rem;">📅 Login From</label>
            <input type="date" name="date_from" class="form-input" value="{date_from}" style="width: 100%; padding: 0.75rem;">
          </div>
          
          <!-- Date To -->
          <div>
            <label style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.8); font-weight: 500; font-size: 0.9rem;">📅 Login To</label>
            <input type="date" name="date_to" class="form-input" value="{date_to}" style="width: 100%; padding: 0.75rem;">
          </div>
        </div>
      </div>
    </form>
    """
  
    # Show search results info
    if search_query:
        if filtered_users:
            html += f"""
            <div class="success-message" style="margin-bottom: 1.5rem;">
                🔍 Search Results for: <strong>{search_query}</strong>
                <span style="float: right;">Found {len(filtered_users)} user(s)</span>
                <br>
                <a href="/ui/{sessionUUID}/user" 
                   style="display: inline-block; 
                          margin-top: 0.5rem; 
                          padding: 0.5rem 1rem; 
                          background: rgba(255, 255, 255, 0.1); 
                          border: 1px solid rgba(255, 255, 255, 0.2); 
                          border-radius: 8px; 
                          color: #00d4ff; 
                          text-decoration: none; 
                          font-weight: 500;
                          transition: all 0.3s ease;">
                   Clear Search
                </a>
            </div>
            """
        else:
            html += f"""
            <div class="error-message" style="text-align: center; margin-bottom: 1.5rem;">
                🔍 No users found matching: <strong>{search_query}</strong>
                <br>
                <a href="/ui/{sessionUUID}/user" 
                   style="display: inline-block; 
                          margin-top: 0.5rem; 
                          padding: 0.5rem 1rem; 
                          background: rgba(255, 255, 255, 0.1); 
                          border: 1px solid rgba(255, 255, 255, 0.2); 
                          border-radius: 8px; 
                          color: #00d4ff; 
                          text-decoration: none; 
                          font-weight: 500;
                          transition: all 0.3s ease;">
                   Show all users
                </a>
            </div>
            """
    
    html += '<ul class="user-list">'
    


    html += '<ul class="user-list">'

    for u in filtered_users:
      enabled_status = '✅ Enabled' if u['enabled'] else '❌ Disabled'
      last_login_text = "Recently Registered"
      if u.get('last_login') is not None:
          try:
              from datetime import datetime
              if isinstance(u['last_login'], str) and u['last_login'].strip():
                  last_login_text = u['last_login']
              elif hasattr(u['last_login'], 'strftime'):
                  last_login_text = u['last_login'].strftime("%Y-%m-%d %H:%M")
              else:
                  last_login_text = str(u['last_login'])
          except:
              last_login_text = str(u['last_login'])
      
      # GET USER TASK STATISTICS
      user_stats = app.stats.getUserStats(u['id'])
      
      if user_stats:
        total_tasks = user_stats['total_tasks']
        finished_tasks = user_stats['finished_tasks']
        running_tasks = user_stats['running_tasks']
        failed_tasks = user_stats['failed_tasks']
      else:
        total_tasks = finished_tasks = running_tasks = failed_tasks = 0
      
      html += f"""
<li class="user-card" style="display: flex; justify-content: space-between; align-items: flex-start; padding: 1.5rem; background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(30, 41, 59, 0.6)); border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid rgba(76, 205, 196, 0.2); transition: all 0.3s ease;">
  <div style="flex-grow: 1;">
    <a href='/ui/{sessionUUID}/user/{u['id']}' class="user-link" style="color: #00d4ff; font-weight: 600; text-decoration: none; font-size: 1.1rem; display: block; margin-bottom: 0.5rem;">
      {u['name']} ({enabled_status})
    </a>
    <div style="color: #94a3b8; font-size: 0.95rem; font-weight: 400; margin-bottom: 1rem;">
      🕒 Last Login: {last_login_text}
    </div>
    
    <!-- TASK STATISTICS SECTION -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
      <!-- Total Tasks Card -->
      <div style="background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 10px; padding: 1rem; text-align: center;">
        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-bottom: 0.3rem; font-weight: 600;">Total Tasks</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #00d4ff;">{total_tasks}</div>
      </div>
      
      <!-- Finished Tasks Card -->
      <div style="background: rgba(78, 205, 196, 0.1); border: 1px solid rgba(78, 205, 196, 0.3); border-radius: 10px; padding: 1rem; text-align: center;">
        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-bottom: 0.3rem; font-weight: 600;">✅ Finished</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #4ecdc4;">{finished_tasks}</div>
      </div>
      
      <!-- Running Tasks Card -->
      <div style="background: rgba(255, 165, 0, 0.1); border: 1px solid rgba(255, 165, 0, 0.3); border-radius: 10px; padding: 1rem; text-align: center;">
        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-bottom: 0.3rem; font-weight: 600;">⚙️ Running</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #ffa500;">{running_tasks}</div>
      </div>
      
      <!-- Failed Tasks Card -->
      <div style="background: rgba(255, 107, 107, 0.1); border: 1px solid rgba(255, 107, 107, 0.3); border-radius: 10px; padding: 1rem; text-align: center;">
        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-bottom: 0.3rem; font-weight: 600;">❌ Failed</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #ff6b6b;">{failed_tasks}</div>
      </div>
    </div>
  </div>

  <form action="/ui/{sessionUUID}/user/{u['id']}/delete" method="POST" onsubmit="return confirm('Are you sure you want to delete user {u['name']}?');" style="margin-left: 1rem;">
    <button type="submit" style="background: none; border: none; color: #f87171; font-size: 1.25rem; cursor: pointer; padding: 0.95rem;">❌</button>
  </form>
</li>
"""
    
    # Message if no users found
    if not filtered_users and not search_query:
        html += """
        <div class="error-message" style="text-align: center;">
            👥 No users found in the system.
        </div>
        """
    
    html += '</ul>'
    html += '</div>'
    
    return htmlBase(html, title="Research Network", sessionUUID=sessionUUID, include_styles=True)

#     for u in filtered_users:
#       enabled_status = '✅ Enabled' if u['enabled'] else '❌ Disabled'
#       last_login_text = "Recently Registered"
#       if u.get('last_login'):
#           try:
#               from datetime import datetime
#               if isinstance(u['last_login'], str):
#                   last_login_text = u['last_login']
#               else:
#                   last_login_text = u['last_login'].strftime("%Y-%m-%d %H:%M")
#           except:
#               last_login_text = str(u['last_login'])
#       html += f"""
# <li class="user-card" style=
#    "display: flex;
#     justify-content: space-between;
#     align-items: flex-start;
#     padding: 1rem; 
#     background: #1e293b; 
#     border-radius: 8px; 
#     margin-bottom: 1rem;
#     ">
#   <div style="flex-grow: 1;">
#     <a href='/ui/{sessionUUID}/user/{u['id']}' class="user-link" style="color: #00d4ff; font-weight: 600; text-decoration: none; font-size: 1.1rem; display: block; margin-bottom: 0.5rem;">
#       {u['name']} ({enabled_status})
#     </a>
#     <div style="color: #94a3b8; font-size: 1.25rem; font-weight: 400; font-family: 'New Century Schoolbook', monospace;">
#       🕒 Last Login: {last_login_text}
#     </div>
#   </div>

#   <form action="/ui/{sessionUUID}/user/{u['id']}/delete" method="POST" onsubmit="return confirm('Are you sure you want to delete user {u['name']}?');" style="margin-left: 1rem;">
#     <button type="submit" style="background: none; border: none; color: #f87171; font-size: 1.25rem; cursor: pointer;padding: 0.95rem;">❌</button>
#   </form>
# </li>
# """
    
#     # Message if no users found
#     if not filtered_users and not search_query:
#         html += """
#         <div class="error-message" style="text-align: center;">
#             👥 No users found in the system.
#         </div>
#         """
    
#     html += '</ul>'
    
#     html += '</div>'
    
#     return htmlBase(html, title="Research Network", sessionUUID=sessionUUID, include_styles=True)

  @webapp.post("/ui/<sessionUUID>/user/add")
  def entrypoint_ui_insert_user(sessionUUID):
    admin_check = check_admin_access(sessionUUID)
    if admin_check:
        return admin_check

    newUserName = request.form["name"]

    return htmlBase(
      '<div class="content-card"><div class="error-message">⚠️ User creation module is in quantum development phase.</div></div>', 
      title="Add Researcher", sessionUUID=sessionUUID, include_styles=True
    )

  @webapp.get("/ui/<sessionUUID>/user/<userIdText>")
  def entrypoint_ui_show_user(sessionUUID, userIdText):
    admin_check = check_admin_access(sessionUUID)
    if admin_check:
        return admin_check

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
      html += f"<tr><th>Email</th><td>{user[5] if user[5] else 'Not set'}</td></tr>"
      html += f"<tr><th>Date of Birth</th><td>{user[6] if user[6] else 'Not set'}</td></tr>"
      html += f"<tr><th>Role</th><td>{user[7] if user[7] else 'Not set'}</td></tr>"
      html += f"<tr><th>Admin User</th><td>{'True' if user[3] else 'False'}</td></tr>"
      html += f"<tr><th>Enabled</th><td>{'True' if user[4] else 'False'}</td></tr>"
      html += '</table>'
      
      html += f"""
      <style>
        /* Custom dropdown styling for user details page */
        select.form-input option {{
          background: #1a1a2e;
          color: white;
          padding: 12px;
        }}
        
        select.form-input:focus {{
          border-color: #00d4ff;
          background: rgba(255, 255, 255, 0.08);
          box-shadow: 0 0 30px rgba(0, 212, 255, 0.3),
                      inset 0 1px 0 rgba(255, 255, 255, 0.1);
          transform: translateY(-2px);
        }}
        
        select.form-input:hover {{
          border-color: rgba(255, 255, 255, 0.3);
          background: rgba(255, 255, 255, 0.07);
        }}
      </style>
      """
      
      html += f"""
      <form action='/ui/{sessionUUID}/user/{user[0]}' method='POST' style='margin-top: 1.5rem;'>
        <input type='hidden' name='action' value='update-role' />
        <div class='form-group'>
          <label for='isAdmin' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>Admin Privilege</label>
          <select name='isAdmin' id='isAdmin' class='form-input'>
            <option value='1' {'selected' if user[3] else ''}>Admin User</option>
            <option value='0' {'' if user[3] else 'selected'}>Regular User</option>
          </select>
        </div>
        <button type='submit' class='login-btn' style='margin-top: 1rem;'>Update Role</button>
      </form>
      """

      html += f"""
  <form action='/ui/{sessionUUID}/user/{user[0]}' method='POST' style='margin-top: 1.5rem;'>
    <input type='hidden' name='action' value='update-enabled' />
    <div class='form-group'>
      <label for='enabled' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>Account Enabled Status</label>
      <select name='enabled' id='enabled' class='form-input'>
        <option value='1' {'selected' if user[4] else ''}>Enabled</option>
        <option value='0' {'' if user[4] else 'selected'}>Disabled</option>
      </select>
    </div>
    <button type='submit' class='login-btn' style='margin-top: 1rem;'>Update Enabled Status</button>
  </form>
  """
      
      html += f"""
      <form action='/ui/{sessionUUID}/user/{user[0]}' method='POST' style='margin-top: 1.5rem;'>
        <input type='hidden' name='action' value='update-details' />
        <div class='form-group'>
          <label for='name' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>User Name</label>
          <input type='text' id='name' name='name' class='form-input' value='{user[1]}' 
                 style='width: 100%; padding: 1rem; background: rgba(255, 255, 255, 0.05); border: 2px solid rgba(255, 255, 255, 0.1); border-radius: 12px; color: white; font-size: 1rem; transition: all 0.3s ease;' />
        </div>
        <div class='form-group'>
          <label for='password' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>New Password (optional)</label>
          <input type='password' id='password' name='password' class='form-input' 
                 style='width: 100%; padding: 1rem; background: rgba(255, 255, 255, 0.05); border: 2px solid rgba(255, 255, 255, 0.1); border-radius: 12px; color: white; font-size: 1rem; transition: all 0.3s ease;' />
        </div>
        <div class='form-group'>
          <label for='password2' style='display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;'>Confirm Password</label>
          <input type='password' id='password2' name='password2' class='form-input' 
                 style='width: 100%; padding: 1rem; background: rgba(255, 255, 255, 0.05); border: 2px solid rgba(255, 255, 255, 0.1); border-radius: 12px; color: white; font-size: 1rem; transition: all 0.3s ease;' />
        </div>
        <button type='submit' class='login-btn' style='margin-top: 1rem;'>Save Changes</button>
      </form>
      """

      html += '</div>'
      return htmlBase(html, title=f"Profile: {user[1]}", sessionUUID=sessionUUID, include_styles=True)
    else:
      return htmlBase(
        '<div class="content-card"><div class="error-message">❌ Researcher profile not found in quantum database.</div></div>', 
        title="Profile Access", sessionUUID=sessionUUID, include_styles=True
      )


  @webapp.post("/ui/<sessionUUID>/user/<userIdText>/delete")
  def entrypoint_ui_remove_user(sessionUUID, userIdText):
    admin_check = check_admin_access(sessionUUID)
    if admin_check:
        return admin_check
    
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
    admin_check = check_admin_access(sessionUUID)
    if admin_check:
        return admin_check

    userId = int(userIdText)
    if f"{userId}" != userIdText:
      return htmlBase("<p>This item was not found.</p>", sessionUUID=sessionUUID)

    action = request.form.get("action", "update-details")

    # Handle role update
    if action == "update-role":
      newIsAdmin = request.form.get("isAdmin")
      is_admin_val = 1 if str(newIsAdmin) in ["1", "true", "True", "on", "yes"] else 0

      updated = app.user.updateUserRole(userId, is_admin_val)
      user = app.user.getUser(userId)

      if updated and user is not None:
        return htmlBase(
          f"""
          <div class='content-card'>
            <div class='success-message'>✅ The user <strong>{user[1]}</strong> role was updated to <strong>{'Admin' if user[3] else 'User'}</strong>.</div>
            <a href='/ui/{sessionUUID}/user' class='action-link'>Back to Users</a>
          </div>
          """,
          sessionUUID=sessionUUID,
          include_styles=True,
          title="Role Updated"
        )
      else:
        return htmlBase(
          f"""
          <div class='content-card'>
            <div class='error-message'>❌ Unable to update role for user ID {userId}.</div>
            <a href='/ui/{sessionUUID}/user/{userId}' class='action-link'>Back to Profile</a>
          </div>
          """,
          sessionUUID=sessionUUID,
          include_styles=True,
          title="Update Failed"
        )
  
    
    # Handle enabled status update
    elif action == "update-enabled":
      newEnabled = request.form.get("enabled")
      enabled_val = 1 if str(newEnabled) in ["1", "true", "True", "on", "yes"] else 0

      updated = app.user.updateUserEnabled(userId, enabled_val, sessionUUID)
      user = app.user.getUser(userId)

      if updated and user is not None:
        return htmlBase(
          f"""
          <div class='content-card'>
            <div class='success-message'>✅ The user <strong>{user[1]}</strong> enabled status was updated to <strong>{'Enabled' if user[4] else 'Disabled'}</strong>.</div>
            <a href='/ui/{sessionUUID}/user' class='action-link'>Back to Users</a>
          </div>
          """,
          sessionUUID=sessionUUID,
          include_styles=True,
          title="Enabled Status Updated"
        )
      else:
        return htmlBase(
          f"""
          <div class='content-card'>
            <div class='error-message'>❌ Unable to update enabled status for user ID {userId}.</div>
            <a href='/ui/{sessionUUID}/user/{userId}' class='action-link'>Back to Profile</a>
          </div>
          """,
          sessionUUID=sessionUUID,
          include_styles=True,
          title="Update Failed"
        )
    
    # Default: update user details (name/password)
    new_name = request.form.get("name", "").strip()
    pw1 = request.form.get("password", "")
    pw2 = request.form.get("password2", "")

    user = app.user.getUser(userId)
    if user is None:
      return htmlBase("<p>This item was not found.</p>", sessionUUID=sessionUUID)

    messages = []
    ok = True

    if new_name and new_name != user[1]:
      if not app.user.updateUserName(userId, new_name):
        ok = False
        messages.append("❌ Failed to update user name (maybe already taken?)")
      else:
        messages.append("✅ User name updated")

    if pw1:
      if pw1 != pw2:
        ok = False
        messages.append("❌ Passwords do not match")
      else:
        if not app.user.updateUserPassword(userId, pw1):
          ok = False
          messages.append("❌ Failed to update password")
        else:
          messages.append("✅ Password updated")

    # Refresh user
    user = app.user.getUser(userId)

    status_block = (
      f"<div class='success-message'>{' '.join(messages) if messages else 'No changes made.'}</div>"
      if ok
      else f"<div class='error-message'>{' '.join(messages)}</div>"
    )

    return htmlBase(
      f"""
      <div class='content-card'>
        {status_block}
        <a href='/ui/{sessionUUID}/user/{userId}' class='action-link'>Back to Profile</a>
      </div>
      """,
      sessionUUID=sessionUUID,
      include_styles=True,
      title="User Updated"
    )


  @webapp.get("/ui/login")
  def entrypoint_ui_login():
    return showPleaseLogin()

  @webapp.post("/ui/login")
  def entrypoint_ui_dologin():
    if "userName" not in request.form or "pass" not in request.form:
        return htmlBase(f"""
        <div class="login-card">
            <div class="login-header">
                <h1 class="login-title">AlphaFold</h1>
                <p class="login-subtitle">Protein Structure Prediction System</p>
            </div>
            
            <div class="error-message" style="margin-bottom: 1.5rem;">
                ❌ Username and password are required.
            </div>
            
            <form action="/ui/login" method="POST" id="loginForm">
                <div class="form-group">
                    <label for="userName" style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;">Username</label>
                    <input type="text" id="userName" name="userName" class="form-input" autocomplete="username" required />
                </div>
                
                <div class="form-group">
                    <label for="pass" style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;">Password</label>
                    <div style="position: relative;">
                        <input type="password" id="pass" name="pass" class="form-input" autocomplete="current-password" required 
                               style="padding-right: 3rem;">
                        <button type="button" id="togglePassword" 
                                onclick="togglePasswordVisibility('pass', 'togglePassword')"
                                style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); 
                                       background: none; border: none; color: rgba(255,255,255,0.6); 
                                       cursor: pointer; font-size: 1.2rem; padding: 0.25rem;">
                            👁️
                        </button>
                    </div>
                </div>
                
                <button type="submit" class="login-btn" style="margin-top: 1rem;">Login</button>
            </form>
            
            <div style="text-align: center; margin-top: 2rem; color: rgba(255,255,255,0.6); font-size: 0.9rem;">
                Need an account? Contact an administrator for access.
            </div>
            
            <script>
            function togglePasswordVisibility(inputId, buttonId) {{
                const passwordInput = document.getElementById(inputId);
                const toggleButton = document.getElementById(buttonId);
                
                if (passwordInput.type === 'password') {{
                    passwordInput.type = 'text';
                    toggleButton.innerHTML = '🙈';
                    toggleButton.title = 'Hide password';
                }} else {{
                    passwordInput.type = 'password';
                    toggleButton.innerHTML = '👁️';
                    toggleButton.title = 'Show password';
                }}
            }}
            </script>
        </div>
        """, title="Login Failed", include_styles=True)
    
    userName = request.form["userName"]
    password = request.form["pass"]
    
    login_result = app.user.doLogin(userName, password)
    
    if login_result.get("success") and login_result.get("sessionUUID"):
        # Login successful, redirect to homepage
        return redirect(f"/ui/{login_result['sessionUUID']}/home")
    
    error_message = login_result.get("error", "Login failed. Please try again.")
    remaining_seconds = login_result.get("remaining_seconds")

    try:
        timer_value = int(remaining_seconds)
    except:
        timer_value = 0

    if timer_value > 0:
       error_message = ""  
    
    # Prepare the error HTML
    error_html = ""
    if error_message:
       error_html = (
        '<div class="error-message" style="margin-bottom: 1.5rem;">'
        f'❌ {error_message}'
        '</div>'
    )

    timer_html = ""
    timer_script = ""

    if timer_value > 0:
        timer_html = """
        <div id="lockout-timer"
             style="color:#ff6b6b;font-weight:bold;margin-bottom:20px;
                    text-align:center;font-size:1.2rem;
                    background:rgba(255,107,107,0.1);
                    border:1px solid #ff6b6b;
                    padding:15px;border-radius:8px;">
            ⏳ Account locked. Initializing timer...
        </div>
        """

        timer_value_js = str(timer_value)  # total seconds remaining
        timer_script = """
        <script>
        (function () {
        var totalSeconds = """ + timer_value_js + """;
        function startTimer() {
        var timerEl = document.getElementById("lockout-timer");
        if (!timerEl) return;
        function tick() {
            var minutes = Math.floor(totalSeconds / 60);
            var seconds = totalSeconds % 60;
            var secondsStr = seconds < 10 ? "0" + seconds : seconds;
            timerEl.innerHTML = "⏳ Account locked. Try again in " + minutes + ":" + secondsStr;
            if (totalSeconds <= 0) {
                window.location.href = "/ui/login";
                return;
            }
            totalSeconds--;
        }
        tick();
        setInterval(tick, 1000);
    }
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", startTimer);
    } else {
        startTimer();
        }
    })();
    </script>
   """
    
        return htmlBase(f"""
        <div class="login-card">
            <div class="login-header">
                <h1 class="login-title">AlphaFold</h1>
                <p class="login-subtitle">Protein Structure Prediction System</p>
            </div>
            
           {error_html}
           {timer_html}
           {timer_script}
            
            <form action="/ui/login" method="POST" id="loginForm">
                <div class="form-group">
                    <label for="userName" style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;">Username</label>
                    <input type="text" id="userName" name="userName" class="form-input" value="{userName}" autocomplete="username" required />
                </div>
                
                <div class="form-group">
                    <label for="pass" style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;">Password</label>
                    <div style="position: relative;">
                        <input type="password" id="pass" name="pass" class="form-input" autocomplete="current-password" required 
                               style="padding-right: 3rem;">
                        <button type="button" id="togglePassword" 
                                onclick="togglePasswordVisibility('pass', 'togglePassword')"
                                style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); 
                                       background: none; border: none; color: rgba(255,255,255,0.6); 
                                       cursor: pointer; font-size: 1.2rem; padding: 0.25rem;">
                            👁️
                        </button>
                    </div>
                </div>
                
                <button type="submit" class="login-btn" style="margin-top: 1rem;">Login</button>
            </form>
            
            <div style="text-align: center; margin-top: 2rem; color: rgba(255,255,255,0.6); font-size: 0.9rem;">
                Need an account? Contact an administrator for access.
            </div>
            
            <script>
            function togglePasswordVisibility(inputId, buttonId) {{
                const passwordInput = document.getElementById(inputId);
                const toggleButton = document.getElementById(buttonId);
                
                if (passwordInput.type === 'password') {{
                    passwordInput.type = 'text';
                    toggleButton.innerHTML = '🙈';
                    toggleButton.title = 'Hide password';
                }} else {{
                    passwordInput.type = 'password';
                    toggleButton.innerHTML = '👁️';
                    toggleButton.title = 'Show password';
                }}
            }}
            </script>
        </div>
        """, title="Login Failed", include_styles=True)
    
    return htmlBase(f"""
<div class="login-card">
    <div class="login-header">
        <h1 class="login-title">AlphaFold</h1>
        <p class="login-subtitle">Protein Structure Prediction System</p>
    </div>

    {error_html}

    <form action="/ui/login" method="POST" id="loginForm">
        <div class="form-group">
            <label for="userName">Username</label>
            <input type="text" id="userName" name="userName"
                   class="form-input" value="{userName}" required />
        </div>

        <div class="form-group">
            <label for="pass">Password</label>
            <input type="password" id="pass" name="pass"
                   class="form-input" required />
        </div>

        <button type="submit" class="login-btn">Login</button>
    </form>
</div>
""", title="Login Failed", include_styles=True)



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
    admin_check = check_admin_access(sessionUUID)
    if admin_check:
        return admin_check
    
    return htmlBase(f"""           
    <div class="login-card">
        <div class="login-header">
            <h1 class="login-title">Register New User</h1>
            <p class="login-subtitle">Create a new AlphaFold user account</p>
        </div>
        
        <form action='/ui/{sessionUUID}/register' method='POST' id="registerForm">
            <div class="form-group">
                <label for='userName' style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;">Username</label>
                <input type='text' id='userName' name='userName' class="form-input" autocomplete="username" required />
            </div>
            
            <div class="form-group">
                <label for='password' style="display: block; margin-bottom: 0.5rem; color: rgba(255,255,255,0.9); font-weight: 600; font-size: 0.9rem;">Password</label>
                <div style="position: relative;">
                    <input type='password' id='password' name='password' class="form-input" autocomplete="new-password" required 
                           style="padding-right: 3rem;">
                    <button type="button" id="toggleRegisterPassword" 
                            onclick="togglePasswordVisibility('password', 'toggleRegisterPassword')"
                            style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); 
                                   background: none; border: none; color: rgba(255,255,255,0.6); 
                                   cursor: pointer; font-size: 1.2rem; padding: 0.25rem;">
                        👁️
                    </button>
                </div>
            </div>
            
            <div class="form-group" style="display: flex; align-items: center; gap: 0.5rem; padding: 1rem; background: rgba(255, 255, 255, 0.05); border: 2px solid rgba(255, 255, 255, 0.1); border-radius: 12px; margin-bottom: 1.5rem;">
                <input type='checkbox' id='isAdmin' name='isAdmin' style='width: 20px; height: 20px; cursor: pointer;' />
                <label for='isAdmin' style='color: rgba(255,255,255,0.9); font-weight: 500; font-size: 0.95rem; cursor: pointer;'>
                    Grant Administrator Privileges
                </label>
            </div>
            
            <button type='submit' class="login-btn" style="margin-top: 0.5rem;">Register User</button>
        </form>
        
        <div style="text-align: center; margin-top: 2rem;">
            <a href='/ui/{sessionUUID}/user' 
               style="display: inline-flex; 
                      align-items: center; 
                      gap: 0.5rem; 
                      padding: 0.75rem 1.5rem; 
                      background: rgba(255, 255, 255, 0.1); 
                      border: 1px solid rgba(255, 255, 255, 0.2); 
                      border-radius: 12px; 
                      color: #00d4ff; 
                      text-decoration: none; 
                      font-weight: 600;
                      font-size: 0.95rem;
                      transition: all 0.3s ease;">
                ← Back to User Management
            </a>
        </div>
        
        <script>
        function togglePasswordVisibility(inputId, buttonId) {{
            const passwordInput = document.getElementById(inputId);
            const toggleButton = document.getElementById(buttonId);
            
            if (passwordInput.type === 'password') {{
                passwordInput.type = 'text';
                toggleButton.innerHTML = '🙈';
                toggleButton.title = 'Hide password';
            }} else {{
                passwordInput.type = 'password';
                toggleButton.innerHTML = '👁️';
                toggleButton.title = 'Show password';
            }}
        }}
        
        document.getElementById('registerForm')?.addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                this.submit();
            }}
        }});
        </script>
    </div>
    """, title="Register User", include_styles=True)
  
  @webapp.post("/ui/<sessionUUID>/register")
  def entrypoint_ui_register_user(sessionUUID):
    admin_check = check_admin_access(sessionUUID)
    if admin_check:
        return admin_check

    userName = request.form.get("userName", "").strip()
    password = request.form.get("password", "").strip()
    is_admin_flag = 1 if request.form.get("isAdmin") in ["on", "1", "true", "True"] else 0

    if not userName or not password:
        return htmlBase(f"""
        <div class="login-card">
            <div class="login-header">
                <h1 class="login-title">Registration Error</h1>
            </div>
            
            <div class="error-message" style="margin-bottom: 1.5rem;">
                ❌ Username and password are required to create an account.
            </div>
            
            <div style="text-align: center; margin-top: 2rem;">
                <a href='/ui/{sessionUUID}/register' 
                   style="display: inline-flex; 
                          align-items: center; 
                          gap: 0.5rem; 
                          padding: 0.75rem 1.5rem; 
                          background: rgba(255, 255, 255, 0.1); 
                          border: 1px solid rgba(255, 255, 255, 0.2); 
                          border-radius: 12px; 
                          color: #00d4ff; 
                          text-decoration: none; 
                          font-weight: 600;
                          font-size: 0.95rem;
                          transition: all 0.3s ease;">
                    🔄 Try Again
                </a>
            </div>
        </div>
        """, title="Registration Error", include_styles=True)

    created = app.user.registerUser(userName, password, is_admin_flag)

    if created:
        return htmlBase(f"""
        <div class="login-card">
            <div class="login-header">
                <h1 class="login-title">Registration Successful</h1>
            </div>
            
            <div class="success-message" style="margin-bottom: 1.5rem;">
                ✅ User <strong>{userName}</strong> has been successfully registered.
                <br>
                <small style="opacity: 0.8;">Account Type: {'Administrator' if is_admin_flag else 'Regular User'}</small>
            </div>
            
            <div style="display: flex; flex-direction: column; gap: 1rem; margin-top: 2rem;">
                <a href='/ui/{sessionUUID}/register' 
                   style="display: inline-flex; 
                          align-items: center; 
                          gap: 0.5rem; 
                          padding: 0.75rem 1.5rem; 
                          background: rgba(255, 255, 255, 0.1); 
                          border: 1px solid rgba(255, 255, 255, 0.2); 
                          border-radius: 12px; 
                          color: #00d4ff; 
                          text-decoration: none; 
                          font-weight: 600;
                          font-size: 0.95rem;
                          transition: all 0.3s ease;
                          justify-content: center;">
                    👤 Register Another User
                </a>
                <a href='/ui/{sessionUUID}/user' 
                   style="display: inline-flex; 
                          align-items: center; 
                          gap: 0.5rem; 
                          padding: 0.75rem 1.5rem; 
                          background: #00d4ff; 
                          border: 1px solid #00d4ff; 
                          border-radius: 12px; 
                          color: #0a0a0a; 
                          text-decoration: none; 
                          font-weight: 700;
                          font-size: 0.95rem;
                          transition: all 0.3s ease;
                          justify-content: center;">
                    👥 View All Users
                </a>
            </div>
        </div>
        """, title="Registration Successful", include_styles=True)
    else:
        return htmlBase(f"""
        <div class="login-card">
            <div class="login-header">
                <h1 class="login-title">Registration Failed</h1>
            </div>
            
            <div class="error-message" style="margin-bottom: 1.5rem;">
                ❌ The username <strong>{userName}</strong> may already exist or there was a system error.
            </div>
            
            <div style="text-align: center; margin-top: 2rem;">
                <a href='/ui/{sessionUUID}/register' 
                   style="display: inline-flex; 
                          align-items: center; 
                          gap: 0.5rem; 
                          padding: 0.75rem 1.5rem; 
                          background: rgba(255, 255, 255, 0.1); 
                          border: 1px solid rgba(255, 255, 255, 0.2); 
                          border-radius: 12px; 
                          color: #00d4ff; 
                          text-decoration: none; 
                          font-weight: 600;
                          font-size: 0.95rem;
                          transition: all 0.3s ease;">
                    🔄 Try Different Username
                </a>
            </div>
        </div>
        """, title="Registration Failed", include_styles=True)
  
  
  @webapp.get("/ui/<sessionUUID>/profile")
  def entrypoint_ui_profile(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    user_data = app.user.getUserOwnProfile(sessionUUID)
    if not user_data:
        return htmlBase("""
        <div class="content-card">
            <div class="error-message">
                ❌ Unable to load profile information.
                <br>
                <a href="/ui/login" class="action-link">Return to Login</a>
            </div>
        </div>
        """, title="Profile Error", include_styles=True)
    
    return showUserProfile(sessionUUID, user_data)

  @webapp.post("/ui/<sessionUUID>/profile/change-password")
  def entrypoint_ui_change_password(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    current_password = request.form.get("current_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    
    # Validation
    if not current_password or not new_password or not confirm_password:
        user_data = app.user.getUserOwnProfile(sessionUUID)
        try:
            _ = user_data[7]
        except IndexError:
            user_data = list(user_data)
            while len(user_data) < 8:
                user_data.append("")
            user_data = tuple(user_data)
        return showChangePassword(sessionUUID, user_data, "All password fields are required.")
    
    if new_password != confirm_password:
        user_data = app.user.getUserOwnProfile(sessionUUID)
        try:
            _ = user_data[7]
        except IndexError:
            user_data = list(user_data)
            while len(user_data) < 8:
                user_data.append("")
            user_data = tuple(user_data)
        return showChangePassword(sessionUUID, user_data, "New passwords do not match.")
    
    if len(new_password) < 6:
        user_data = app.user.getUserOwnProfile(sessionUUID)
        try:
            _ = user_data[7]
        except IndexError:
            user_data = list(user_data)
            while len(user_data) < 8:
                user_data.append("")
            user_data = tuple(user_data)
        return showChangePassword(sessionUUID, user_data, "New password must be at least 6 characters long.")
    
    # Attempt to change password
    success = app.user.updateOwnPassword(sessionUUID, current_password, new_password)
    
    user_data = app.user.getUserOwnProfile(sessionUUID)
    try:
        _ = user_data[7]
    except IndexError:
        user_data = list(user_data)
        while len(user_data) < 8:
            user_data.append("")
        user_data = tuple(user_data)
    
    if success:
        return showChangePassword(sessionUUID, user_data, "", "Password changed successfully!")
    else:
        return showChangePassword(sessionUUID, user_data, "Failed to change password. Please check your current password.", "")
    

  @webapp.post("/ui/<sessionUUID>/profile/edit-details")
  def entrypoint_ui_edit_details(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    # Get current user
    current_user = app.user.getUserFromSession(sessionUUID)
    if not current_user:
        return showPleaseLogin()
    
    # Get form data
    new_name = request.form.get("edit_name", "").strip()
    new_email = request.form.get("edit_email", "").strip()
    new_dob = request.form.get("edit_dob", "").strip()
    new_role = request.form.get("edit_role", "").strip()
    
    # Validate username is required
    if not new_name:
        user_data = app.user.getUserOwnProfile(sessionUUID)
        try:
            _ = user_data[7]
        except IndexError:
            user_data = list(user_data)
            while len(user_data) < 8:
                user_data.append("")
            user_data = tuple(user_data)
        return showEditProfile(sessionUUID, user_data, "Username is required.")
    
    # Check if username is changing
    current_name = current_user["name"]
    username_changed = new_name != current_name
    
    # If username changed, check if it's available
    if username_changed:
        try:
            from app.dbUtil import getDbInstance
            mydb_temp = getDbInstance()
            mycursor_temp = mydb_temp.cursor()
            mycursor_temp.execute(app_constants.SQL_SELECT_USER_BY_NAME, [new_name])
            existing_user = mycursor_temp.fetchone()
            if existing_user:
                user_data = app.user.getUserOwnProfile(sessionUUID)
                try:
                    _ = user_data[7]
                except IndexError:
                    user_data = list(user_data)
                    while len(user_data) < 8:
                        user_data.append("")
                    user_data = tuple(user_data)
                return showEditProfile(sessionUUID, user_data, "Username already exists. Please choose a different one.")
        except Exception as e:
            trace(f"Error checking username availability: {e}")
    
    dob_for_db = ""
    if new_dob:
        try:
            parts = new_dob.split("-")
            if len(parts) == 3:
                if len(parts[0]) == 4 and len(parts[1]) == 2 and len(parts[2]) == 2:
                    dob_for_db = new_dob  # Already in correct format
                else:
                    if len(parts[0]) == 2 and len(parts[1]) == 2 and len(parts[2]) == 4:
                        dob_for_db = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    else:
                        dob_for_db = new_dob
        except:
            dob_for_db = new_dob
    
    # Update user details
    success = app.user.updateUserDetails(
        current_user["id"], 
        new_name,
        new_email, 
        dob_for_db if dob_for_db else None, 
        new_role
    )
    
    # Get updated user data for profile page
    user_data = app.user.getUserOwnProfile(sessionUUID)
    
    if success:
        return showUserProfile(sessionUUID, user_data, "success", "Profile details updated successfully!")
    else:
        error_msg = "Failed to update profile details due to no changes."
        return showUserProfile(sessionUUID, user_data, "error", error_msg)
    
  @webapp.get("/ui/<sessionUUID>/profile/edit")
  def entrypoint_ui_edit_profile(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    user_data = app.user.getUserOwnProfile(sessionUUID)
    if not user_data:
        return htmlBase("""
        <div class="content-card">
            <div class="error-message">
                ❌ Unable to load profile information.
                <br>
                <a href="/ui/login" class="action-link">Return to Login</a>
            </div>
        </div>
        """, title="Profile Error", include_styles=True)
    
    try:
        _ = user_data[7]
    except IndexError:
        user_data = list(user_data)
        while len(user_data) < 8:
            user_data.append("")
        user_data = tuple(user_data)
    
    return showEditProfile(sessionUUID, user_data)
  
  
  @webapp.get("/ui/<sessionUUID>/profile/change-password")
  def entrypoint_ui_change_password_page(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    user_data = app.user.getUserOwnProfile(sessionUUID)
    if not user_data:
        return htmlBase("""
        <div class="content-card">
            <div class="error-message">
                ❌ Unable to load profile information.
                <br>
                <a href="/ui/login" class="action-link">Return to Login</a>
            </div>
        </div>
        """, title="Profile Error", include_styles=True)
    
    try:
        _ = user_data[7]
    except IndexError:
        user_data = list(user_data)
        while len(user_data) < 8:
            user_data.append("")
        user_data = tuple(user_data)
    
    return showChangePassword(sessionUUID, user_data)
  

  @webapp.get("/ui/<sessionUUID>/home")
  def entrypoint_ui_homepage(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    user = app.user.getUserFromSession(sessionUUID)
    if not user:
        return showPleaseLogin()
    
    return showHomepage(sessionUUID, user["name"], user["is_admin"])
  
  @webapp.get("/ui/<sessionUUID>/messages")
  def entrypoint_ui_messages(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    current_user = app.user.getUserFromSession(sessionUUID)
    return showMessages(sessionUUID, current_user["id"])

  @webapp.get("/ui/<sessionUUID>/messages/compose")
  def entrypoint_ui_compose(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    return showComposeMessage(sessionUUID)

  @webapp.post("/ui/<sessionUUID>/messages/send")
  def entrypoint_ui_send_message(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    current_user = app.user.getUserFromSession(sessionUUID)
    recipient_id = request.form.get("recipient_id")
    subject = request.form.get("subject")
    msg_text = request.form.get("message")
    
    app.user.sendMessage(current_user["id"], recipient_id, subject, msg_text)
    return redirect(f"/ui/{sessionUUID}/messages")

  @webapp.get("/ui/<sessionUUID>/support")
  def entrypoint_ui_support(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    current_user = app.user.getUserFromSession(sessionUUID)
    return showSupportTickets(sessionUUID, current_user["id"], current_user["is_admin"])

  @webapp.get("/ui/<sessionUUID>/support/new")
  def entrypoint_ui_new_support(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    return showNewSupportTicket(sessionUUID)

  @webapp.post("/ui/<sessionUUID>/support/new")
  def entrypoint_ui_create_support(sessionUUID):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    current_user = app.user.getUserFromSession(sessionUUID)
    subject = request.form.get("subject")
    description = request.form.get("description")
    priority = request.form.get("priority", "medium")
    
    app.user.createSupportTicket(current_user["id"], subject, description, priority)
    return redirect(f"/ui/{sessionUUID}/support")
  # Add these route handlers in userUi.py inside the createEntrypoints function

  @webapp.post("/ui/<sessionUUID>/messages/<messageId>/delete")
  def entrypoint_ui_delete_message(sessionUUID, messageId):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    current_user = app.user.getUserFromSession(sessionUUID)
    try:
        msg_id = int(messageId)
        app.user.deleteMessage(msg_id, current_user["id"])
    except Exception as e:
        app.user.trace(f"Error deleting message: {e}")
    
    return redirect(f"/ui/{sessionUUID}/messages")


  @webapp.get("/ui/<sessionUUID>/messages/<messageId>/toggle-read")
  def entrypoint_ui_toggle_read(sessionUUID, messageId):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    try:
        msg_id = int(messageId)
        mycursor.execute("SELECT is_read FROM af_messages WHERE id = %s", [msg_id])
        result = mycursor.fetchone()
        
        if result:
            new_status = not result[0]
            mycursor.execute("UPDATE af_messages SET is_read = %s WHERE id = %s", 
                           [new_status, msg_id])
            mydb.commit()
    except Exception as e:
        app.user.trace(f"Error toggling read status: {e}")
    
    return redirect(f"/ui/{sessionUUID}/messages")


  @webapp.get("/ui/<sessionUUID>/messages/<messageId>")
  def entrypoint_ui_view_message(sessionUUID, messageId):
    if not app.user.isLoggedIn(sessionUUID):
        return showPleaseLogin()
    
    current_user = app.user.getUserFromSession(sessionUUID)
    
    try:
        msg_id = int(messageId)
        # Mark as read when viewing
        app.user.markMessageRead(msg_id)
        
        # Get the message details
        mycursor.execute("""
            SELECT m.id, m.sender_id, u.name as sender_name, m.subject, m.message, 
                   m.message_type, m.is_read, m.created_at
            FROM af_messages m
            JOIN af_users u ON m.sender_id = u.id
            WHERE m.id = %s
        """, [msg_id])
        msg = mycursor.fetchone()
        
        if not msg:
            return redirect(f"/ui/{sessionUUID}/messages")
        
        # Safely access message fields
        msg_id = msg[0] if len(msg) > 0 else 0
        sender_name = msg[2] if len(msg) > 2 else "Unknown"
        subject = msg[3] if len(msg) > 3 else "(No subject)"
        message_text = msg[4] if len(msg) > 4 else ""
        created_at = msg[7] if len(msg) > 7 else ""
        
        html = f"""
        <div class="content-card">
            <div style="margin-bottom: 2rem;">
                <a href='/ui/{sessionUUID}/messages' 
                   style="color: #00d4ff; text-decoration: none; font-size: 1.2rem;">
                    ← Back to Messages
                </a>
            </div>
            
            <div style="background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 16px; 
                        border-left: 4px solid #4ecdc4;">
                <h1 style="color: #00d4ff; margin-bottom: 1rem; font-size: 1.8rem;">
                    {subject}
                </h1>
                
                <div style="color: rgba(255,255,255,0.7); margin-bottom: 1.5rem; 
                            padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div style="margin-bottom: 0.5rem;">
                        <strong>From:</strong> {sender_name}
                    </div>
                    <div>
                        <strong>Date:</strong> {created_at}
                    </div>
                </div>
                
                <div style="color: white; font-size: 1.1rem; line-height: 1.8; 
                            white-space: pre-wrap;">
                    {message_text}
                </div>
            </div>
            
            <div style="display: flex; gap: 1rem; margin-top: 2rem;">
                <form action='/ui/{sessionUUID}/messages/{msg_id}/delete' method='POST' 
                      onsubmit="return confirm('Are you sure you want to delete this message?');">
                    <button type='submit' 
                            style="padding: 0.75rem 1.5rem; background: #ff6b6b; color: white; 
                                   border: none; border-radius: 12px; font-weight: 600; 
                                   cursor: pointer; transition: all 0.3s ease;">
                        🗑️ Delete Message
                    </button>
                </form>
            </div>
        </div>
        """
        
        return htmlBase(html, title="View Message", sessionUUID=sessionUUID, include_styles=True)
        
    except Exception as e:
        app.user.trace(f"Error viewing message: {e}")
        return redirect(f"/ui/{sessionUUID}/messages")
