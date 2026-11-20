DNF_RESPONSE = ({"status": "not found"}, 404)
# Join tasks with users (UI only)
SQL_SELECT_TASKS_WITH_USER = """
SELECT
  t.*,  
  u.name AS user_name
FROM af_tasks t
JOIN af_users u ON t.userId = u.id
"""
SQL_SELECT_USERS_ORDERED = """
SELECT id, name
FROM af_users
ORDER BY name
"""

MAX_FAILED_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 0.5

AF_TASKS_KEYS = [
    "id",
    "enabled",
    "userId",
    "name",
    "userComment",
    "fasta",
    "model_preset",
    "full_dbs",
    "models_to_relax",
    "enable_gpu_relax",
    "max_template_date"
]

AF_TASKS_KEYS_WITH_USER = AF_TASKS_KEYS + ["user_name"]

AF_USERS_KEYS = [
    "id",
    "name",
    "user_password",
    "is_admin",
    "enabled",
    "failed_attempts",
    "locked_until",
    "email",
    "date_of_birth",
    "role",
    "last_login"
]

AF_SUPPORT_TICKETS_KEYS = [
    "id",
    "user_id",
    "subject",
    "description",
    "status",
    "priority",
    "created_at",
    "updated_at"
]

AF_TASKS_INPUT_KEYS = {
    "enabled" : "enabled",
    "userId": "userId",
    "task_name": "name",
    "user_comment": "userComment",
    "fasta": "fasta",
    "preset": "modelPreset",
    "dbs": "fullDBS",
    "models_to_relax": "modelsToRelax",
    "gpu_relax": "enableGpuRelax",
    "template_date": "maxTemplateDate"
}

AF_TASKS_INPUT_KEYS_TO_DB = {
    "enabled" : "enabled",
    "userId": "userId",
    "name": "name",
    "userComment": "usercomment",
    "fasta": "fasta",
    "modelPreset": "model_preset",
    "fullDBS": "full_dbs",
    "modelsToRelax": "models_to_relax",
    "enableGpuRelax": "enable_gpu_relax",
    "maxTemplateDate": "max_template_date"
}

ALLOWED_UPDATE_FIELDS = (
    "name",
    "userId",
    "usercomment",
    "fasta",
    "model_preset",
    "full_dbs",
    "models_to_relax",
    "enable_gpu_relax",
    "max_template_date"
)

PLEASE_LOGIN = ({ "status": "please login", "url": ["/api/1.0/login"] }, 403)

SQL_DELETE_TASK = "DELETE FROM af_tasks WHERE af_tasks.id = %s"

SQL_SELECT_TASKS = "SELECT * FROM af_tasks"

SQL_SELECT_USERS = "SELECT * FROM af_users"

SQL_SELECT_SESSIONS = "SELECT * FROM af_sessions"

SQL_INSERT_TASK = """
      INSERT INTO af_tasks (
          enabled,
          userId,
          name,
          usercomment,
          fasta,
          model_preset,
          full_dbs,
          models_to_relax,
          enable_gpu_relax,
          max_template_date
      ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """

SQL_SELECT_TASK_BY_ID = "SELECT * FROM af_tasks WHERE af_tasks.id = %s"

SQL_SELECT_USER_BY_NAME = "SELECT id, name, user_password, is_admin, enabled, failed_attempts, locked_until, email, date_of_birth, role, last_login FROM af_users WHERE af_users.name = %s"

SQL_SELECT_USER_BY_ID = "SELECT id, name, user_password, is_admin, enabled, failed_attempts, locked_until, email, date_of_birth, role, last_login FROM af_users WHERE af_users.id = %s"

SQL_INSERT_SESSION = """INSERT INTO af_sessions (id, userId, expires_at, session_status)
                          VALUES (%s, %s, %s, %s);
                    """
# Message SQL queries
SQL_INSERT_MESSAGE = """
    INSERT INTO af_messages (sender_id, recipient_id, subject, message, message_type)
    VALUES (%s, %s, %s, %s, %s)
"""

SQL_SELECT_USER_MESSAGES = """
    SELECT m.id, m.sender_id, u.name as sender_name, m.subject, m.message, 
           m.message_type, m.is_read, m.created_at
    FROM af_messages m
    JOIN af_users u ON m.sender_id = u.id
    WHERE m.recipient_id = %s OR (m.recipient_id IS NULL AND m.message_type = 'broadcast')
    ORDER BY m.created_at DESC
"""

SQL_MARK_MESSAGE_READ = "UPDATE af_messages SET is_read = TRUE WHERE id = %s"

SQL_DELETE_MESSAGE = "DELETE FROM af_messages WHERE id = %s"

SQL_COUNT_UNREAD_MESSAGES = """
    SELECT COUNT(*) FROM af_messages 
    WHERE recipient_id = %s AND is_read = FALSE
"""

# Support ticket SQL
SQL_INSERT_SUPPORT_TICKET = """
    INSERT INTO af_support_tickets (user_id, subject, description, priority)
    VALUES (%s, %s, %s, %s)
"""

SQL_SELECT_USER_TICKETS = """
    SELECT id, user_id, subject, description, status, priority, created_at, updated_at
    FROM af_support_tickets 
    WHERE user_id = %s 
    ORDER BY created_at DESC
"""

SQL_SELECT_ALL_TICKETS = """
    SELECT t.id, t.user_id, t.subject, t.description, t.status, t.priority, t.created_at, t.updated_at, u.name as user_name 
    FROM af_support_tickets t
    JOIN af_users u ON t.user_id = u.id
    ORDER BY t.created_at DESC
"""

SQL_UPDATE_TICKET_STATUS = """
    UPDATE af_support_tickets SET status = %s WHERE id = %s
"""
SQL_SELECT_ACTIVE_SESSION_BY_ID = """
                          SELECT s.id, s.userId, s.expires_at, s.created_at, s.session_status,
                              u.name, u.is_admin, u.enabled
                          FROM
                              af_sessions AS s
                          JOIN
                              af_users AS u ON s.userId = u.id
                          WHERE
                              s.id = %s
                              AND s.expires_at > NOW();  
                    """

SQL_DELETE_INACTIVE_SESSIONS = "DELETE FROM af_sessions WHERE expires_at < NOW()"

SQL_UPDATE_INACTIVE_SESSION = "UPDATE af_sessions SET session_status = 0 WHERE id = %s"

SQL_UPDATE_USER_LAST_LOGIN = "UPDATE af_users SET last_login = NOW() WHERE id = %s"

SQL_INSERT_USER_BY_NAME = "INSERT INTO af_users (name, user_password, is_admin, enabled) VALUES (%s, %s, %s, %s)"

SQL_DELETE_USER_BY_ID = "DELETE FROM af_users WHERE id = %s"

SQL_UPDATE_USER_ROLE = "UPDATE af_users SET is_admin = %s WHERE id = %s"

SQL_UPDATE_USER_NAME = "UPDATE af_users SET name = %s WHERE id = %s"

SQL_UPDATE_USER_PASSWORD = "UPDATE af_users SET user_password = %s WHERE id = %s"

SQL_UPDATE_USER_ENABLED = "UPDATE af_users SET enabled = %s WHERE id = %s"

SQL_UPDATE_USER_EMAIL = "UPDATE af_users SET email = %s WHERE id = %s"

SQL_UPDATE_USER_DOB = "UPDATE af_users SET date_of_birth = %s WHERE id = %s"

SQL_UPDATE_USER_ROLE_TEXT = "UPDATE af_users SET role = %s WHERE id = %s"

SQL_UPDATE_USER_DETAILS = "UPDATE af_users SET name = %s, email = %s, date_of_birth = %s, role = %s WHERE id = %s"

SQL_SELECT_LOGIN_ATTEMPTS = "SELECT failed_attempts, locked_until FROM af_users WHERE id = %s"

SQL_INCREMENT_LOGIN_ATTEMPTS = "UPDATE af_users SET failed_attempts = %s WHERE id = %s"

SQL_LOCK_USER_ACCOUNT = "UPDATE af_users SET failed_attempts = %s, locked_until = %s WHERE id = %s"

SQL_RESET_LOGIN_ATTEMPTS = "UPDATE af_users SET failed_attempts = 0, locked_until = NULL WHERE id = %s"

SESSION_EXPIRY_HOURS = 2

SESSION_ACTIVE = 1

JS_SCRIPTS = """
    <script src="/static/js/tasks.js"></script>

    <script>
      // Create floating particles
      function createParticles() {
        const particles = document.querySelector('.particles');
        if (!particles) return;
        
        for (let i = 0; i < 50; i++) {
          const particle = document.createElement('div');
          particle.className = 'particle';
          particle.style.left = Math.random() * 100 + '%';
          particle.style.top = Math.random() * 100 + '%';
          particle.style.animationDelay = Math.random() * 6 + 's';
          particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
          particles.appendChild(particle);
        }
      }
      
      document.addEventListener('DOMContentLoaded', createParticles);
    </script>

"""

TASK_DETAILS_JS_HELPERS = """
<script>
  function yn(v) {
    return Number(v || 0) === 1 ? "Yes" : "No";
  }

  function safe(v, empty = "-") {
    if (v === null || v === undefined) return empty;
    const s = String(v).trim();
    return s ? s : empty;
  }

  function toDateOnly(v) {
    if (!v) return "-";
    const s = String(v);
    if (s.includes("T")) return s.split("T")[0];
    return s;
  }
</script>




"""

CSS_STYLES = """

    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
      
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #0a0a0a;
        overflow-x: hidden;
        color: white;
        min-height: 100vh;
        position: relative;
      }
      
      /* Animated Background */
      .bg-animation {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -2;
        background: linear-gradient(45deg, #0a0a0a, #1a1a2e, #16213e, #0f3460);
        background-size: 400% 400%;
        animation: gradientShift 8s ease infinite;
      }
      
      @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
      
      /* Floating Particles */
      .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
      }
      
      .particle {
        position: absolute;
        width: 2px;
        height: 2px;
        background: #00d4ff;
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
        opacity: 0.7;
      }
      
      .particle:nth-child(odd) {
        background: #ff6b6b;
        animation-delay: -2s;
      }
      
      .particle:nth-child(3n) {
        background: #4ecdc4;
        animation-delay: -4s;
      }
      
      @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.7; }
        50% { transform: translateY(-20px) rotate(180deg); opacity: 1; }
      }
      
/* Header - Enhanced Modern Design */
      .header {
        position: sticky;
        top: 0;
        background: linear-gradient(135deg, rgba(10, 10, 10, 0.95), rgba(20, 20, 40, 0.95));
        backdrop-filter: blur(20px) saturate(180%);
        border-bottom: 2px solid transparent;
        border-image: linear-gradient(90deg, #00d4ff, #ff6b6b, #4ecdc4, #00d4ff) 1;
        padding: 1rem 3rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        z-index: 1000;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        animation: slideDown 0.5s ease-out;
      }
      
      @keyframes slideDown {
        from {
          transform: translateY(-100%);
          opacity: 0;
        }
        to {
          transform: translateY(0);
          opacity: 1;
        }
      }
      
      .logo {
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff 0%, #ff6b6b 50%, #4ecdc4 100%);
        background-size: 200% 200%;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        position: relative;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        animation: gradientShiftText 8s ease infinite;
      }
      
      @keyframes gradientShiftText {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
      }
      
      .logo::before {
        content: "⚛";
        font-size: 2.5rem;
        background: linear-gradient(135deg, #00d4ff, #ff6b6b);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-right: 0.25rem;
        animation: rotateLogo 4s linear infinite;
      }
      
      @keyframes rotateLogo {
        0%, 100% { transform: rotate(0deg); }
        50% { transform: rotate(180deg); }
      }
      
      .logo:hover {
        transform: scale(1.05);
        filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5));
      }
      
      /* Enhanced Navigation Menu - Glass Morphism Style */
      .nav-menu {
        display: flex;
        gap: 0.75rem;
        align-items: center;
        background: rgba(255, 255, 255, 0.03);
        padding: 0.75rem 1rem;
        border-radius: 20px;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 
          0 8px 32px rgba(0, 0, 0, 0.3),
          inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
      }
      
      .nav-menu::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
        transition: left 0.5s ease;
      }
      
      .nav-menu:hover::before {
        left: 100%;
      }

      .nav-menu .btn {
        padding: 0.75rem 1.5rem;
        font-size: 0.9rem;
        font-weight: 600;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.9);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        text-decoration: none;
        white-space: nowrap;
      }
      
      .nav-menu .btn::before {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.3), transparent);
        transform: translate(-50%, -50%);
        transition: width 0.4s ease, height 0.4s ease;
      }
      
      .nav-menu .btn:hover::before {
        width: 300px;
        height: 300px;
      }

      .nav-menu .btn:hover {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(78, 205, 196, 0.15));
        border-color: #00d4ff;
        color: #00d4ff;
        transform: translateY(-3px);
        box-shadow: 
          0 6px 20px rgba(0, 212, 255, 0.4),
          0 0 40px rgba(0, 212, 255, 0.2);
      }
      
      .nav-menu .btn:active {
        transform: translateY(-1px);
      }

      /* Special styling for logout button */
      .nav-menu .logout-btn {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(255, 107, 107, 0.1));
        border: 1px solid rgba(255, 107, 107, 0.3);
        color: #ff6b6b;
        margin-left: 0.5rem;
      }
      
      .nav-menu .logout-btn::before {
        background: radial-gradient(circle, rgba(255, 107, 107, 0.3), transparent);
      }

      .nav-menu .logout-btn:hover {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.3), rgba(255, 107, 107, 0.2));
        border-color: #ff6b6b;
        color: white;
        box-shadow: 
          0 6px 20px rgba(255, 107, 107, 0.4),
          0 0 40px rgba(255, 107, 107, 0.2);
      }

      /* Admin section with special container */
      .admin-section {
        display: flex;
        gap: 0.75rem;
        padding-left: 0.75rem;
        margin-left: 0.75rem;
        border-left: 2px solid rgba(0, 212, 255, 0.3);
        position: relative;
      }
      
      .admin-section::before {
        content: "ADMIN";
        position: absolute;
        top: -12px;
        left: 0.5rem;
        font-size: 0.6rem;
        color: #00d4ff;
        font-weight: 700;
        letter-spacing: 1px;
        background: rgba(10, 10, 10, 0.95);
        padding: 0 0.5rem;
      }

      /* Admin buttons special styling */
   .nav-menu .admin-btn {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(236, 72, 153, 0.15));
    border: 1px solid rgba(167, 139, 250, 0.4);
    color: #c084fc;
    }

   .nav-menu .admin-btn::before {
    background: radial-gradient(circle, rgba(139, 92, 246, 0.3), transparent);
    }

   .nav-menu .admin-btn:hover {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(236, 72, 153, 0.25));
    border-color: #a78bfa;
    color: #f0abfc;
    box-shadow: 
    0 6px 20px rgba(139, 92, 246, 0.5),
    0 0 40px rgba(167, 139, 250, 0.3);
}

      /* Badge for unread messages - Enhanced */
      .badge {
        background: linear-gradient(135deg, #ff6b6b, #ff5555);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-left: 0.4rem;
        box-shadow: 0 2px 8px rgba(255, 107, 107, 0.5);
        animation: badgePulse 2s infinite;
        position: relative;
      }
      
      .badge::before {
        content: "";
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(135deg, #ff6b6b, #ff5555);
        border-radius: 12px;
        z-index: -1;
        opacity: 0;
        animation: badgeGlow 2s infinite;
      }

      @keyframes badgePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }
      
      @keyframes badgeGlow {
        0%, 100% { opacity: 0; }
        50% { opacity: 0.6; filter: blur(8px); }
      }

      /* Responsive Design */
      @media (max-width: 1200px) {
        .header {
          padding: 1rem 2rem;
        }
        
        .nav-menu {
          gap: 0.5rem;
          padding: 0.6rem 0.8rem;
        }
        
        .nav-menu .btn {
          padding: 0.6rem 1.2rem;
          font-size: 0.85rem;
        }
        
        .logo {
          font-size: 1.6rem;
        }
      }
      
      @media (max-width: 768px) {
        .header {
          padding: 0.75rem 1rem;
          flex-direction: column;
          gap: 1rem;
        }
        
        .nav-menu {
          width: 100%;
          justify-content: center;
          flex-wrap: wrap;
          gap: 0.4rem;
          padding: 0.5rem;
        }
        
        .nav-menu .btn {
          padding: 0.5rem 1rem;
          font-size: 0.8rem;
        }
        
        .admin-section {
          margin-left: 0;
          padding-left: 0;
          border-left: none;
          width: 100%;
          justify-content: center;
        }
        
        .admin-section::before {
          display: none;
        }
      }

      /* Base button style for navigation */
      .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.75rem 1.5rem;
        font-size: 0.9rem;
        font-weight: 600;
        text-decoration: none;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        border: 1px solid transparent;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        min-width: 90px;
        text-align: center;
        cursor: pointer;
        backdrop-filter: blur(10px);
      }

      /* Login Button */
      .btn[href*="login"], .btn[href*="Login"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
      }

      .btn[href*="login"]:hover, .btn[href*="Login"]:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        border-color: rgba(102, 126, 234, 0.6);
      }

      /* Register Button */
      .btn[href*="register"], .btn[href*="Register"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: 1px solid rgba(240, 147, 251, 0.3);
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.2);
      }

      .btn[href*="register"]:hover, .btn[href*="Register"]:hover {
        background: linear-gradient(135deg, #e785f0 0%, #f04558 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.4);
        border-color: rgba(240, 147, 251, 0.6);
      }

      /* User List Button & Task List Button*/
      .btn[href*="user"], a[href*="user"],
       .btn[href*="tasks"], a[href*="tasks"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: 1px solid rgba(79, 172, 254, 0.3);
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.2);
        text-decoration: none;
        padding: 0.75rem 1.5rem;
        font-size: 0.9rem;
        font-weight: 600;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        backdrop-filter: blur(10px);
        display: inline-flex;
        align-items: center;
        position: relative;
        overflow: hidden;
        min-width: 90px;
        text-align: center;
        cursor: pointer;
      }
      .btn[href*="tasks"], a[href*="tasks"]{
      background: linear-gradient(135deg, #4ecdc4 0%, #00f2fe 100%);
      }

      .float-right
      {
        float:right;
      }

      .btn[href*="user"]:hover, a[href*="user"]:hover {
        background: linear-gradient(135deg, #3d91e8 0%, #00d4e8 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4);
        border-color: rgba(79, 172, 254, 0.6);
      }

      /* Logout Button */
     .nav-menu .logout-btn {
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(249, 115, 22, 0.15));
  border: 1px solid rgba(251, 146, 60, 0.4);
  color: #fb923c;
  margin-left: 0.5rem;
}

.nav-menu .logout-btn::before {
  background: radial-gradient(circle, rgba(251, 146, 60, 0.3), transparent);
}

.nav-menu .logout-btn:hover {
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.3), rgba(249, 115, 22, 0.25));
  border-color: #fb923c;
  color: #fdba74;
  box-shadow: 
    0 6px 20px rgba(251, 146, 60, 0.5),
    0 0 40px rgba(251, 146, 60, 0.3);
}
      /* Glowing effect for all buttons */
      .btn::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
      }

      .btn:hover::before {
        left: 100%;
      }

      /* Active/Focus states */
      .btn:active {
        transform: translateY(0px);
        transition: transform 0.1s ease;
      }

      .btn:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
      }

      /* Responsive design for smaller screens */
      @media (max-width: 768px) {
        .nav-menu {
          gap: 0.5rem;
        }
        
        .btn {
          padding: 0.6rem 1rem;
          font-size: 0.8rem;
          min-width: 70px;
        }
      }
      
      .nav-link {
        color: rgba(255, 255, 255, 0.8);
        text-decoration: none;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 500;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
      }
      
      .nav-link::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
      }
      
      .nav-link:hover::before {
        left: 100%;
      }
      
      .nav-link:hover {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        transform: translateY(-2px);
      }
      
      .nav-link.logout {
        background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
        color: white;
      }
      
      /* Main Container */
      .container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: calc(100vh - 100px);
        padding: 2rem;
        position: relative;
      }

      /* Password toggle button styling */
      .toggle-password-btn:hover {{
      color: #00d4ff !important;
      background: rgba(0, 212, 255, 0.1) !important;
      border-radius: 4px; }
      }

      .toggle-password-btn:active {{
      transform: translateY(-50%) scale(0.95) !important; }
      }
      
      /* Login Card */
      .login-card {
        background: rgba(15, 15, 15, 0.9);
        backdrop-filter: blur(30px);
        border-radius: 24px;
        padding: 3rem;
        width: 100%;
        max-width: 450px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
        animation: cardAppear 1s ease-out;
        box-shadow: 
          0 25px 50px -12px rgba(0, 0, 0, 0.8),
          0 0 0 1px rgba(255, 255, 255, 0.05);
      }

      
      @keyframes cardAppear {
        from {
          opacity: 0;
          transform: translateY(30px) scale(0.95);
        }
        to {
          opacity: 1;
          transform: translateY(0) scale(1);
        }
      }
      
      .login-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #00d4ff, #ff6b6b, #4ecdc4, #00d4ff);
        background-size: 200% 100%;
        animation: borderGlow 3s ease infinite;
      }
      
      @keyframes borderGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
      }
      
      .login-header {
        text-align: center;
        margin-bottom: 2.5rem;
      }
      
      .login-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff, #00d4ff);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        animation: titleGlow 2s ease-in-out infinite alternate;
      }
      
      @keyframes titleGlow {
        from { filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.3)); }
        to { filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.6)); }
      }
      
      .login-subtitle {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1.1rem;
        font-weight: 400;
      }
      
      .form-group {
        margin-bottom: 2rem;
        position: relative;
      }
      
      .form-input {
        width: 100%;
        padding: 1.25rem 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        color: white;
        font-size: 1rem;
        font-weight: 500;
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
        position: relative;
      }
      
      .form-input::placeholder {
        color: rgba(255, 255, 255, 0.5);
        font-weight: 400;
      }
      
      .form-input:focus {
        outline: none;
        border-color: #00d4ff;
        background: rgba(255, 255, 255, 0.08);
        box-shadow: 
          0 0 30px rgba(0, 212, 255, 0.3),
          inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
      }
      
      .form-label {
        position: absolute;
        left: 1.5rem;
        top: 1.25rem;
        color: rgba(255, 255, 255, 0.6);
        font-size: 1rem;
        font-weight: 500;
        pointer-events: none;
        transition: all 0.3s ease;
        background: rgba(15, 15, 15, 0.9);
        padding: 0 0.5rem;
      }
      
      .form-input:focus + .form-label,
      .form-input:not(:placeholder-shown) + .form-label {
        top: -0.5rem;
        font-size: 0.85rem;
        color: #00d4ff;
      }
      
      .btn-danger {
          background-color: #e74c3c;
          color: white;
          border: none;
          padding: 5px 10px;
          margin-left: 10px;
          cursor: pointer;
        }

      .btn-danger:hover {
        background-color: #c0392b;
      }

      .login-btn {
        width: 100%;
        padding: 1.25rem;
        background: linear-gradient(135deg, #00d4ff, #0099cc);
        color: white;
        border: none;
        border-radius: 16px;
        font-size: 1.1rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 1px;
      }
      
      .login-btn::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.6s ease;
      }
      
      .login-btn:hover::before {
        left: 100%;
      }
      
      .login-btn:hover {
        transform: translateY(-3px);
        box-shadow: 
          0 15px 35px rgba(0, 212, 255, 0.4),
          0 5px 15px rgba(0, 0, 0, 0.3);
        background: linear-gradient(135deg, #00e5ff, #00bcd4);
      }
      
      .login-btn:active {
        transform: translateY(-1px);
      }
      
      /* Messages */
      .success-message {
        background: rgba(76, 205, 196, 0.15);
        border: 1px solid rgba(76, 205, 196, 0.3);
        color: #4ecdc4;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
        animation: messageSlide 0.5s ease-out;
      }
      
      .error-message {
        background: rgba(255, 107, 107, 0.15);
        border: 1px solid rgba(255, 107, 107, 0.3);
        color: #ff6b6b;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
        animation: messageSlide 0.5s ease-out;
      }
      
      @keyframes messageSlide {
        from {
          opacity: 0;
          transform: translateX(-20px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
      
      /* Content Cards */
      .content-card {
        background: rgba(15, 15, 15, 0.9);
        backdrop-filter: blur(30px);
        border-radius: 24px;
        padding: 2.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 1rem;
        max-width: 1000px;
        width: 100%;
        animation: cardAppear 0.8s ease-out;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        text-align: center;
      }
      
      .action-link {
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        background: linear-gradient(135deg, #4ecdc4, #44a08d);
        color: white;
        text-decoration: none;
        font-weight: 600;
        padding: 1rem 2rem;
        border-radius: 16px;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
      }
      
      .action-link::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
      }
      
      .action-link:hover::before {
        left: 100%;
      }
      
      .action-link:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(78, 205, 196, 0.4);
      }
      
      /* User Lists */
      .user-list {
        list-style: none;
        padding: 0;
        display: grid;
        gap: 1rem;
      }
      
      .user-list li a {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: rgba(255, 255, 255, 0.05);
        color: white;
        text-decoration: none;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.4s ease;
        font-weight: 500;
        backdrop-filter: blur(10px);
      }
      
      .user-list li a::before {
        content: "👤";
        font-size: 1.5rem;
        filter: grayscale(100%);
        transition: filter 0.3s ease;
      }
      
      .user-list li a:hover::before {
        filter: none;
      }
      
      .user-list li a:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: #00d4ff;
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 212, 255, 0.2);
      }
      
      /* Tables */
      .user-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1.5rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
      }
      
      .user-table th,
      .user-table td {
        padding: 1.25rem;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      }
      
      .user-table th {
        background: rgba(255, 255, 255, 0.05);
        font-weight: 600;
        color: #00d4ff;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
      }
      
      .user-table td {
        color: rgba(255, 255, 255, 0.9);
      }
      
      .user-table tr:last-child td {
        border-bottom: none;
      }
      
      /* Generate particles dynamically */
      .particles {
        pointer-events: none;
      }

      .user-card {
        position: relative;
        background: #1e293b;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        list-style: none;
        display: flex;
        align-items: center;
      }

      .user-link {
        color: #00d4ff;
        font-weight: 600;
        text-decoration: none;
        flex-grow: 1;
      }

      .delete-form {
        margin-left: auto;
      }

      .delete-btn {
        background: none;
        border: none;
        color: #f87171;
        font-size: 1.25rem;
        cursor: pointer;
        transition: transform 0.2s ease;
      }

      .delete-btn:hover {
        transform: scale(1.2);
      }

      .tasks-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
      }

      .tasks-title {
        margin: 0;
        color: #00d4ff;
        font-size: 2rem;
        font-weight: 700;
      }

      .tasks-table-wrapper {
        margin-top: 0.75rem;
        overflow-x: auto;
        border-radius: 12px;
        border: 1px solid #2e3239;
        overflow-y: hidden;
        -webkit-overflow-scrolling: touch;
      }

      .tasks-table {
        width: 100%;
        border-collapse: collapse;
        border-spacing: 0;
      }

      .tasks-table thead th {
        padding: 0.7rem 1rem;
        text-align: center;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #00d4ff;
        background: #24272d;
        border-bottom: 1px solid #2e3239;
      }

      .tasks-table tbody td {
        padding: 0.7rem 1rem;
        text-align: center;
        font-size: 0.85rem;
        color: #e5e7eb;
        border-bottom: 1px solid #2e3239;
      }

      .tasks-table tbody tr:nth-child(odd) {
        background-color: #1c1f24;
      }

      .tasks-table tbody tr:nth-child(even) {
        background-color: #24272d;
      }

      .tasks-table tbody tr:hover {
        background-color: #2e3239;
      }

      .tasks-enabled-cell {
        font-size: 1rem;
      }

      .btn-small {
        padding: 0.35rem 0.9rem;
        font-size: 0.8rem;
      }

      select.form-input option {
        background: #1a1a2e;
        color: white;
        padding: 12px;
      }
      
      select.form-input {
        background: rgba(26, 26, 46, 0.8) !important;
        color: white !important;
        appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2300d4ff' d='M6 9L1 4h10z'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: right 1rem center !important;
        padding-right: 3rem !important;
      }
      
      input[type="date"].form-input {
        background: rgba(26, 26, 46, 0.8) !important;
        color: white !important;
        color-scheme: dark;
      }
      
      input[type="date"].form-input::-webkit-calendar-picker-indicator {
        filter: invert(1);
        cursor: pointer;
      }
      
      select.form-input:focus,
      input[type="date"].form-input:focus {
        border-color: #00d4ff;
        background: rgba(26, 26, 46, 0.9) !important;
      }
      
      select.form-input:hover,
      input[type="date"].form-input:hover {
        border-color: rgba(255, 255, 255, 0.3);
        background: rgba(26, 26, 46, 0.85) !important;
      }
      
      .tasks-table a[href*="tasks"] {
          all: unset;
          cursor: pointer;
      }
     
      .icon-btn {
        display: inline-flex !important;
        justify-content: center;
        align-items: center;
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: transparent;
        border: none;
        cursor: pointer;
        text-decoration: none;
      }

      .svg-icon {
        width: 30px;
        height: 30px;
        transform-origin: center;
        fill: #00d4ff;
        transition: fill 0.2s ease;
      }

      .svg-icon--details {
        transform: scale(1.1);
      }

      .svg-icon--edit, .svg-icon--eye, .svg-icon--download {
        transform: scale(0.8);
      }
      
      .svg-icon--delete {
        transform: scale(0.7);
        fill: #ff4d4f;
      }

      .icon-btn:hover .svg-icon--delete {
        fill: #ff7875;
      }

      .icon-btn:hover .svg-icon {
        fill: #fff;
      }
      
      /* Tooltip container */
      .tooltip {
        position: relative !important;
      }

      /* Tooltip bubble */
      .tooltip::after {
        content: attr(data-tooltip);
        position: absolute;
        left: 50%;
        bottom: calc(100% - 2px);
        transform: translateX(-50%);
        white-space: nowrap;
        background: #0b1120;
        color: #e5e7eb;
        font-size: 0.75rem;
        padding: 0.3rem 0.6rem;
        border-radius: 9999px;
        border: 1px solid #1f2937;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.15s ease, transform 0.15s ease;
        z-index: 20;
      }

      /* Small arrow */
      .tooltip::before {
        content: "";
        position: absolute;
        left: 50%;
        bottom: calc(100% - 10px);
        transform: translateX(-50%);
        border-width: 6px;
        border-style: solid;
        border-color: #0b1120 transparent transparent transparent;
        opacity: 0;
        transition: opacity 0.15s ease;
        z-index: 19;
      }

      .tooltip:hover::after,
      .tooltip:hover::before {
        opacity: 1;
      }
      
      .tooltip:hover::after {
        transform: translateX(-50%) translateY(-4px);
      }
      
      .switch {
        position: relative;
        display: inline-block;
        width: 44px;
        height: 24px;
      }

      .switch input {
        opacity: 0;
        width: 0;
        height: 0;
      }

      /* Track */
      .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;        /* OFF color */
        transition: 0.2s;
        border-radius: 999px;
      }

      /* Knob */
      .slider:before {
        position: absolute;
        content: "";
        height: 18px;
        width: 18px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: 0.2s;
        border-radius: 50%;
      }

      /* ON state */
      input:checked + .slider {
        background-color: #00d4ff;     /* ON color */
      }

      input:checked + .slider:before {
        transform: translateX(20px);
      }

      /* Disabled (while request is running) */
      input:disabled + .slider {
        opacity: 0.6;
        cursor: not-allowed;
      }

      .task-pr{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        justify-content: space-between;
      }
      
      .task-toggle {
        width: 70%;
        display: flex;
      }

      .task-label{
        color: #00d4ff;
        letter-spacing: 1px;
        font-size: 0.9rem;
      }
      .task-input {
        color: white;
        background-color: #4444446b;
        border: none;
        border-radius: 5px;
        padding: 3px 6px;
        margin-left: 10px;
        width: 70%;
    }
      .task-submit{
        padding: 1.25rem;
        background: linear-gradient(135deg, #00d4ff, #0099cc);
        color: white;
        border: none;
        border-radius: 16px;
        font-size: 1.1rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 20px;
      }
      .task-submit:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0, 212, 255, 0.4), 0 5px 15px rgba(0, 0, 0, 0.3);
        background: linear-gradient(135deg, #00e5ff, #00bcd4);
      }
      
      
      .userselect {
        min-width: 160px;
        max-width: 260px;
        width: auto;
        cursor: pointer;

        height: 44px;
        padding: 0 44px 0 16px;
        border-radius: 14px;

        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;

        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;

        background-color: #2b2b2b;
        color: #fff;

        background-image: url("data:image/svg+xml;utf8,\
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'>\
        <path d='M7 10l5 5 5-5'/></svg>");
        background-repeat: no-repeat;
        background-size: 18px;
        background-position: right 14px center;
      }
      
      .details-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
        text-align: left;
      }

      /* Make some rows span full width */
      .details-grid .full-width{
        grid-column: 1 / -1;
      }

      /* Details row layout */
      .details-grid .task-pr{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        flex-wrap: nowrap;
      }

      /* Label column */
      .details-grid .task-label{
        flex: 0 0 120px;
        text-align: left;
      }

      /* Value column */
      .details-grid .task-value{
        flex: 1;
        background-color: #4444446b;
        border-radius: 5px;
        padding: 8px 10px;
        text-align: left;
        color: white;
        overflow-wrap: anywhere;
      }

      /* For multiline text blocks (FASTA / Comment) */
      .details-grid .task-value-pre{
        white-space: pre-wrap;
        line-height: 1.5;
        margin: 0;
      }
      @media (max-width: 940px) {
        .details-grid {
          grid-template-columns: 1fr; /* one column grid */
        }

        .details-grid .task-pr {
          flex-direction: column; /* label on top, value below */
          align-items: flex-start;
        }

        .details-grid .task-label {
          flex: none;
          width: 100%;
        }

        .details-grid .task-value {
          width: 100%;
        }
      }

    </style>
    
    """
