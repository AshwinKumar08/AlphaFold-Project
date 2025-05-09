#!/usr/bin/python3

from api import apiCall

r = apiCall("/api/1.0/login", body={ "userName": "test_user" })
if r["status"] == "ok":
  sessionUUID = r["sessionUUID"]
else:
  exit(1)

print(apiCall(f"/api/1.0/{sessionUUID}/task"))
