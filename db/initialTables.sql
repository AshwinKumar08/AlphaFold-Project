
CREATE TABLE af_users (
  id               INT           NOT NULL AUTO_INCREMENT,
  name             VARCHAR(64)   NOT NULL UNIQUE,
  user_password    VARCHAR(255)  NOT NULL,
  is_admin         TINYINT       NOT NULL DEFAULT 0,
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

INSERT INTO af_users (name, user_password, is_admin) VALUES ('testuser', '$2b$12$ko9Vd0bgu8Q8YOiFSkA79OtocB1CpYNw065HuslieJPABH.xSBR4a',1);

CREATE TABLE IF NOT EXISTS af_sessions (
    id                  VARCHAR(255) NOT NULL UNIQUE, 
    userId              INT          NOT NULL,
    expires_at          DATETIME     NOT NULL,
    created_at          DATETIME     DEFAULT CURRENT_TIMESTAMP,
    session_status      TINYINT      NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    FOREIGN KEY (userId) REFERENCES af_users(id) ON DELETE CASCADE
);
