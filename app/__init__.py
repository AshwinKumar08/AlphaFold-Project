from datetime import datetime
from http.client import HTTPException
import logging
import uuid
from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

import app.user
import app.task
import app.userUi
# import util

webapp = Flask(__name__)
webapp.wsgi_app = ProxyFix(webapp.wsgi_app, x_for=1, x_host=1)

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"logs/webapp_errors_{datetime.now().strftime('%d_%m_%Y')}.log"),
                        logging.StreamHandler()
                    ])

@webapp.errorhandler(Exception)
def handle_exception(e):
    
    if isinstance(e, HTTPException):
        return e

    error_id = str(uuid.uuid4())
    webapp.logger.exception(f"[{error_id}] An unexpected error occurred:")

    return jsonify({"error": "Internal Server Error", "message": f"Error-Id: {error_id}: An unexpected error occurred."}), 500


@webapp.route("/")
def entrypoint_root(): 
    return userUi.showPleaseLogin()
        


user.createEntrypoints(webapp)
task.createEntrypoints(webapp)
userUi.createEntrypoints(webapp)
