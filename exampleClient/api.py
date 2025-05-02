import json
import http.client

def apiCall(path, method="GET", body=None):
  print(f"Call {path}")
  c = http.client.HTTPConnection('localhost', 5000)
  if body is not None:
    body = bytes(json.dumps(body), "utf8")
  c.request(method, path, body=body)
  response = c.getresponse()
  if response.status == 200:
    return json.loads(response.read())
  else:
    print(f"Failed with code: {response.status}")
    print(response.read())
    exit(2)
