import requests
import msgpack

url = "https://micro-dev.ohbibi.com/api/index/tag"

headers = {
    "X-BB-AppId": "aa0007f1-0b9d-4c4a-be6e-04183c9a7cb8"
}

query = ["file", "save-c39ec9ee-8e54-11e7-b5d9-9963b83f6e06"]
resp = requests.post(url, data=msgpack.packb(query), headers=headers)
print("status: ", str(resp.status_code))
data = msgpack.unpackb(resp.content)

print(str(data))