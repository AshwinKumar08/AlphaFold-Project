from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix

import app.user
import app.task
import app.userUi

webapp = Flask(__name__)
webapp.wsgi_app = ProxyFix( webapp.wsgi_app, x_for=1, x_host=1)



@webapp.route("/")
def entrypoint_root():
  return userUi.showPleaseLogin()


user.createEntrypoints(webapp)
task.createEntrypoints(webapp)
userUi.createEntrypoints(webapp)
