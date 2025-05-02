#!/usr/bin/python3

from api import apiCall

r = apiCall("/login", body={ "userName": "test_user" })
if r["status"] == "ok":
  sessionUUID = r["sessionUUID"]
else:
  exit(1)

print(apiCall(f"/{sessionUUID}/task"))
