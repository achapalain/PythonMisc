
import requests, msgpack, json


def login(profileId = None, accountToken = None):
    identityBundle = None
    if not profileId or not accountToken:
        identityBundle = identityBundleDefault
    else:
        identityBundle = {
            "profileId": profileId,
            "accountToken": accountToken
        }
    print("Login with: " + str(identityBundle))
    requestData = msgpack.packb(identityBundle)
    
    resp = requests.post("https://us-central1-ohbibi-meta-test.cloudfunctions.net/test-auth-login", 
                        headers={"Content-Type": "application/x-msgpack",
                                 "X-BB-AppId": "aa0007f1-0b9d-4c4a-be6e-04183c9a7cb8" # OnlineCore.ApplicationId
                        },
                        data=requestData)
    
    print(resp.status_code)
    print(resp.text.encode('utf-8'))

def getMsgpackEmail(destProfileId, script):

    # Define data
    penaltyData = {
        "value": 0,
        "type": 4,
        "customScript": script
    }
    
    # Convert data to json string
    penaltyDataJson = json.dumps(penaltyData)
    
    # Convert json to bytes
    penaltyDataBytes = bytes(penaltyDataJson, 'utf-8')

    mailEntry = {
        "entryId": None,
        "mailboxId": destProfileId,
        "kind": "penalty",
        "time": None,
        "payload": penaltyDataBytes
    }
    # Compress to msgpack bytes
    return msgpack.packb(mailEntry)

def process():
    # unessesary      
    login()

    script = "\"{\\n\\r\\nLog.Trace(\\\"2=\\\"+Main.CheatsAllowed.ToString());\\r\\nLog.Trace(\\\"3=\\\"+OnlineCore.Env);\\r\\nLog.Trace(\\\"4=\\\"+SupOnlineManager.Instance.IsNetworkAvailable().ToString());\\r\\nLog.Trace(\\\"5=\\\"+AppVersion.VersionName);\\r\\nLog.Trace(\\\"6=\\\"+AppVersion.VersionBuild);\\r\\nLog.Trace(\\\"7=\\\"+AppVersion.IsIPhone.ToString());\\r\\nLog.Trace(\\\"8=\\\"+AppVersion.IsMaster.ToString());\\r\\nLog.Trace(\\\"9=\\\"+AppVersion.IsEditor.ToString());\\r\\nLog.Trace(\\\"10=\\\"+AppVersion.IsPlaying.ToString());\\r\\nLog.Trace(\\\"11=\\\"+AppVersion.Platform);\\r\\nLog.Trace(\\\"12\\\"+AppVersion.RuntimePlatform);\\r\\nif (AppVersion.IsAndroid == true)\\r\\n    Log.Trace(\\\"13=\\\"+AppVersion.AndroidApiLevel.ToString());\\nSystemCore.Instance.SendUserLog();\\n\\rLog.Trace(\\\"fromPython !!\\\");\\r\\n}\""

    dataMsgPack = getMsgpackEmail("26ab9ad0-812e-11e9-952a-f9f456628a89", script)

    print(str(dataMsgPack))

    data_str = '{"text": "Hello nigger"}'
    resp = requests.post("https://ingress-test.obb.cloud/api/mail/add", 
                headers={"Content-Type": "application/x-msgpack",
                         "X-BB-AppId": "aa0007f1-0b9d-4c4a-be6e-04183c9a7cb8", # OnlineCore.ApplicationId
                         # "X-BB-ProfileId": "b516a690-7d35-11e9-969f-71efd7f138cf", # OnlineCore.Instance.ProfileId
                         # "Authorization": "obb VTJGc2RHVmtYMTlyTWlRWnM5WHVUcUZtdzJ6WEJZNVhEQk1Jd1hzWFdzaVA0SHlhREgyZEFGanNmQ0xkNGpxUnh1MXcva2F3NmhicEk2dVMyRVJuZ3kvMGJjYXFZSlorR3pqejNuRkFLSTVoNEdibFBkMndoeHNiUGtneGZyRzlRR3h3Nld0dnNIVW9tc1BZZXBnMUw1Q3lRVnMreUJWbks3Z0ZOOHJWTUtZPQ==" # OnlineCore.Instance.AuthToken
                },
                data=dataMsgPack)
    print(resp.status_code)
    print(resp.text.encode('utf-8'))


    data_str = '{"text": "Hello nigger"}'
    resp = requests.post("https://us-central1-ohbibi-meta-dev.cloudfunctions.net/dev-gpp-blacklisted-words", 
               headers={"Content-Type": "application/json"},
               data=data_str)
    print(resp.status_code)
    print(resp.text)
    
identityBundleDefault = {
        "profileId": "26ab9ad0-812e-11e9-952a-f9f456628a89",
        "accountToken": "CiQA8yC47i/JxieaGlpH9Q5/h0xWXvXObhsilVQKE8QysE3DlT0SdACyg9l5c5FmXpSWhPOUVYg87qqQeftn9F48qYAHUJ+2rM/amArsp37yI6NOPRZwBfQPgku2DCLz9d1MDbO9LNRaCkEbnp6GclR3fDGzrUWBNL6OdC/1aySdNwwsDTiJJZDlKmtyEviHTZtpXuC8X6UjcjF/"
    }
    
if __name__ == "__main__":
    process()