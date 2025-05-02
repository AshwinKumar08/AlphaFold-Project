
CREATE TABLE af_users (
  id    int         not null auto_increment,
  name  varchar(64) not null UNIQUE,
  PRIMARY KEY (id)
);

CREATE TABLE af_tasks (
  id                int         not null auto_increment,
  enabled           tinyint     not null default 0,
  userId            int         not null,
  name              varchar(64) not null default '',
  usercomment       text        not null default '',
  fasta             text        not null default '',
  model_preset      varchar(32) not null default '',
  full_dbs          tinyint     not null default 1,
  models_to_relax   tinyint     not null default 2,
  enable_gpu_relax  tinyint     not null default 1,
  max_template_data varchar(11) not null default '',
  PRIMARY KEY (id),
  FOREIGN KEY (userId) REFERENCES af_users(id)
);


CREATE TABLE af_results (
  id            int         not null,
  state         tinyint     not null default 0,
  results_file  varchar(64) not null default '',
  log_file      varchar(64) not null default '',
  PRIMARY KEY (id),
  FOREIGN KEY (id) REFERENCES af_tasks(id)
);


insert into af_users (name) values ('testuser');
