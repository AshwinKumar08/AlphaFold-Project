
CREATE TABLE af_users (
  id               INT           NOT NULL AUTO_INCREMENT,
  name             VARCHAR(64)   NOT NULL UNIQUE,
  user_password    VARCHAR(255)  NOT NULL,
  is_admin         TINYINT       NOT NULL DEFAULT 0,
  enabled          TINYINT       NOT NULL DEFAULT 1,
  failed_attempts  INT           DEFAULT 0,
  locked_until     DATETIME      DEFAULT NULL,
  email            VARCHAR(255)  DEFAULT '',
  date_of_birth    DATE          DEFAULT NULL,
  role             VARCHAR(64)   DEFAULT '',
  last_login       DATETIME      DEFAULT NULL,
  description      TEXT          DEFAULT '',
  PRIMARY KEY (id)
);

CREATE TABLE af_tasks (
  id                INT         NOT NULL AUTO_INCREMENT,
  enabled           TINYINT     NOT NULL DEFAULT 0,
  userId            INT         NOT NULL,
  name              VARCHAR(64) NOT NULL DEFAULT '',
  usercomment       TEXT        NOT NULL DEFAULT '',
  fasta             TEXT        NOT NULL DEFAULT '',
  model_preset      VARCHAR(32) NOT NULL DEFAULT '',
  full_dbs          TINYINT     NOT NULL DEFAULT 1,
  models_to_relax   TINYINT     NOT NULL DEFAULT 2,
  enable_gpu_relax  TINYINT     NOT NULL DEFAULT 1,
  max_template_date VARCHAR(11) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  FOREIGN KEY (userId) REFERENCES af_users(id) ON DELETE CASCADE
);

CREATE TABLE af_results (
  id            INT         NOT NULL,
  state         TINYINT     NOT NULL DEFAULT 0,
  results_file  VARCHAR(64) NOT NULL DEFAULT '',
  log_file      VARCHAR(64) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES af_tasks(id) ON DELETE CASCADE
);

INSERT INTO af_users (name, user_password, is_admin, enabled) VALUES ('testuser', '$2b$12$ko9Vd0bgu8Q8YOiFSkA79OtocB1CpYNw065HuslieJPABH.xSBR4a',1,1);

CREATE TABLE IF NOT EXISTS af_sessions (
    id                  VARCHAR(255) NOT NULL UNIQUE, 
    userId              INT          NOT NULL,
    expires_at          DATETIME     NOT NULL,
    created_at          DATETIME     DEFAULT CURRENT_TIMESTAMP,
    session_status      TINYINT      NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    FOREIGN KEY (userId) REFERENCES af_users(id) ON DELETE CASCADE
);

CREATE TABLE af_messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sender_id INT NOT NULL,
  recipient_id INT,  -- NULL for broadcasts
  subject VARCHAR(255),
  message TEXT NOT NULL,
  message_type ENUM('user', 'admin', 'broadcast', 'support') DEFAULT 'user',
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (sender_id) REFERENCES af_users(id),
  FOREIGN KEY (recipient_id) REFERENCES af_users(id)
);

CREATE TABLE af_support_tickets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  subject VARCHAR(255) NOT NULL,
  status ENUM('open', 'in_progress', 'closed') DEFAULT 'open',
  priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  description      TEXT          DEFAULT '',
  FOREIGN KEY (user_id) REFERENCES af_users(id)
);
