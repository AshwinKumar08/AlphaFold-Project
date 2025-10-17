DNF_RESPONSE = ({"status": "not found"}, 404)

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

AF_USERS_KEYS = [
    "id",
    "name",
    "user_password",
    "is Admin"
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

SQL_SELECT_USER_BY_NAME = "SELECT id, name, user_password, is_admin FROM af_users WHERE af_users.name = %s"

SQL_SELECT_USER_BY_ID = "SELECT id, name, user_password, is_admin FROM af_users WHERE af_users.id = %s"

SQL_INSERT_SESSION = """INSERT INTO af_sessions (id, userId, expires_at, session_status)
                          VALUES (%s, %s, %s, %s);
                    """

SQL_SELECT_ACTIVE_SESSION_BY_ID = """
                          SELECT s.id, s.userId, s.expires_at, s.created_at, s.session_status,
                              u.name, u.is_admin
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

SQL_INSERT_USER_BY_NAME = "INSERT INTO af_users (name, user_password, is_admin) VALUES (%s, %s, %s)"

SQL_DELETE_USER_BY_ID = "DELETE FROM af_users WHERE id = %s"

SESSION_EXPIRY_HOURS = 2

SESSION_ACTIVE = 1

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
      
      /* Header */
      .header {
        position: relative;
        background: rgba(15, 15, 15, 0.9);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        z-index: 10;
      }
      
      .logo {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #ff6b6b, #4ecdc4);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        position: relative;
      }
      
      .logo::before {
        content: "";
        position: absolute;
        top: -5px;
        left: -5px;
        right: -5px;
        bottom: -5px;
        background: linear-gradient(45deg, #00d4ff, #ff6b6b, #4ecdc4, #00d4ff);
        border-radius: 10px;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: -1;
        filter: blur(10px);
      }
      
      .logo:hover::before {
        opacity: 0.3;
      }
      
      /* Enhanced Navigation Menu Styles */
      .nav-menu {
        display: flex;
        gap: 0.75rem;
        align-items: center;
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

      /* User List Button */
      .btn[href*="user"], a[href*="user"] {
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
      .btn[href*="logout"], a[href*="logout"] {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        color: #333;
        border: 1px solid rgba(255, 154, 158, 0.3);
        box-shadow: 0 4px 15px rgba(255, 154, 158, 0.2);
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
        justify-content: center;
        position: relative;
        overflow: hidden;
        min-width: 90px;
        text-align: center;
        cursor: pointer;
      }

      .btn[href*="logout"]:hover, a[href*="logout"]:hover {
        background: linear-gradient(135deg, #ff8a8e 0%, #f5bfdf 50%, #f5bfdf 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 154, 158, 0.4);
        border-color: rgba(255, 154, 158, 0.6);
        color: #222;
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
        max-width: 900px;
        width: 100%;
        animation: cardAppear 0.8s ease-out;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
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

    </style>
    
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