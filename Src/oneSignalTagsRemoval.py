import obbinstall
from Python import common
from Python import zipUtils
from Python import ioUtils
import os
import requests
import json
import time
import shutil
import csv


class GameConfig:
    def __init__(self, name, app_id, rest_id, valid_tags=None):
        self.name = name
        self.appId = app_id
        self.restId = rest_id
        self.valid_tags = valid_tags


def print_group(*text):
    text = " ".join([str(x) for x in text])
    print("\n###", text)


def print_title(*text):
    text = " ".join([str(x) for x in text])
    print("#", text)


def view_notifications(config):
    url = "https://onesignal.com/api/v1/notifications?app_id={}".format(config.appId)
    # payload = open("request.json")
    headers = {"Authorization": "Basic {}".format(config.restId)}
    r = requests.get(url, "--include", headers=headers)
    content = r.json()
    content = json.dumps(content, indent=2)
    print(content)


def request_csv_export(config):
    print_title("Starting export:", config.name)

    # Start export request
    url = "https://onesignal.com/api/v1/players/csv_export?app_id={}".format(config.appId)
    headers = {
        "Authorization": "Basic {}".format(config.restId),
        "Content-Type": "application/json",
    }
    elapsed_seconds = 0
    while True:
        req = requests.post(url, headers=headers)
        if req.status_code == 400:
            print("\r", end="")
            print("Previous export has not been consumed yet, you need to wait few minutes".format())
            return

        res = req.json()
        if "errors" in res:
            elapsed_seconds += 1
            print("\rWaiting: {}s".format(elapsed_seconds), end="")
            time.sleep(1)
        else:
            print("\r", end="")
            url = res["csv_file_url"]
            print("File URL:", url)
            return url


def download_url(config, url):
    print_title("Downloading:", url)
    file_name = config.name + "." + os.path.basename(url)
    file_name = os.path.abspath(file_name)
    elapsed_seconds = 0
    while True:
        with requests.get(url, stream=True) as req:
            if req.status_code == 403:
                elapsed_seconds += 1
                print("\rWaiting for file preparation (can take a few minutes): {}s".format(elapsed_seconds), end="")
                time.sleep(1)
            else:
                print("\r", end="")
                with open(file_name, 'wb') as f:
                    shutil.copyfileobj(req.raw, f)
                    break
    if req.ok:
        print("File saved => " + file_name)
        return file_name
    else:
        print(req.content)


def extract(path_in, remove_at_end=True):
    print_title("Extracting:", path_in)
    path_out = zipUtils.unzipBigFile(path_in)
    if remove_at_end and path_out and path_out != path_in:
        ioUtils.remove(path_in)
        print("Removed ", path_in)
    print("Extracted to =>", path_out)
    return path_out


def find_all_tags(csv_path):
    output_path = csv_path + ".txt"
    print_title("Finding users to clean up")
    all_tags = set()
    with open(output_path, "w", encoding="utf-8") as f_out:
        with open(csv_path, encoding="utf-8") as f_in:
            reader = csv.reader(f_in, delimiter=',')
            tags_idx = None
            for row in reader:
                if "tags" not in row or "id" not in row:
                    print("Could not find 'tags' token")
                    return
                tags_idx = row.index("tags")
                break
            for row in reader:
                tags = row[tags_idx]
                tags = json.loads(tags)
                for tag in tags:
                    all_tags.add(tag)
        f_out.write(str(all_tags))
        print("All tags found:", all_tags)
    return all_tags


def export_invalid_users_csv(game_config, csv_path, all_tags):
    if not game_config.valid_tags or len(game_config.valid_tags) == 0:
        return
    output_path = csv_path.replace(".csv", ".invalid_users.csv")
    print_title("Finding users to clean up")
    invalid_tags = [x for x in all_tags if x not in game_config.valid_tags]
    csv_player_suffix = "," + ",".join(["" for _ in invalid_tags])
    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write("player_id," + ",".join(invalid_tags) + "\n")
        invalid_player_count = 0
        with open(csv_path, encoding="utf-8") as f_in:
            reader = csv.reader(f_in, delimiter=',')
            id_idx, tags_idx = None, None
            for row in reader:
                if "tags" not in row or "id" not in row:
                    print("Could not find 'tags' token")
                    return
                id_idx = row.index("id")
                tags_idx = row.index("tags")
                break
            for row in reader:
                user_id = row[id_idx]
                user_tags = json.loads(row[tags_idx])
                for tag in user_tags:
                    if tag in invalid_tags:
                        f_out.write(user_id + csv_player_suffix + "\n")
                        invalid_player_count += 1
                        break
        print(invalid_player_count, "players to address")
        print("Exported results:", output_path)
    return output_path


def process_game(game_config):
    print_group(game_config.name)
    game_timer = common.Timer()

    # export_url = request_csv_export(game_config)
    # user_file_zipped = download_url(game_config, export_url)
    # user_file = extract(user_file_zipped)
    # all_tags = find_all_tags(user_file)

    all_tags = None
    user_file = None
    for f in common.getFiles(".", ".txt"):
        if f.startswith(game_config.name):
            content = open(f, encoding="utf-8").readline()
            content = content.replace("'", '"').replace("{", "[").replace("}", "]")
            all_tags = json.loads(content, encoding="utf-8")
            user_file = f.replace(".txt", "")
            break
    export_invalid_users_csv(game_config, user_file, all_tags)
    
    print_title(game_config.name, "- Process time:", game_timer.formatedDuration())


gameConfigs = [
    # GameConfig("Bike",      "74fc63fc-8fd8-469c-9d6b-f23b58877daa", "Nzc3NzVlZGYtNjY5OC00YjgxLWE5ODAtNGNiN2E4ZTBhODU4"),
    # GameConfig("Car",       "b4e6a87e-876b-40f8-a641-b9256d4763c5", "NmU0NTEwMGQtMDg3Mi00ZmFhLTk4ODItNDMyNTBhOGY3NDJi"),
    # GameConfig("Dino",      "83131d87-5d6a-4274-a585-27f892102f56", "NjRkZjhlNGEtNDdiMy00YmMxLWE5NjYtMDQwM2VkYWRjMGMz"),
    # GameConfig("Frag",      "6891c547-2fbe-4b8c-8f07-b80605c7a969", "ODEyY2U0OWUtM2JmOC00NTY1LWJjZWQtZDI5Y2NjMWEyNmQ0", ("profileId" + "buildName" + "dollarSpent")),
    # GameConfig("Frag_TEST", "0e69c8a6-132b-4dad-a63a-9d8c4c899164", "ZjllOWFjYjctM2FlZi00NjM2LTk3YzItZGVhYWZmZWMwNWEz", ("profileId", "buildName" "dollarSpent")),
    # GameConfig("Kart",      "747a094a-3abf-4c43-a9b3-8ebf65458bbb", "YzIzNTk0YTgtNzdlYy00MGZkLTgwMGItNDM3MmZlMTRkOTRi", ("profileId", "buildName", "dollarSpent")),
    # GameConfig("Kart_TEST", "34def3e6-0c69-43ec-a363-1b5e6bb81814", "Y2I1OWI2YTQtZTUzNi00MWY5LTljM2ItMzIwM2FhZDI4MTU1", ("profileId", "buildName", "dollarSpent")),
    GameConfig("Sup",       "175b43b2-6630-464c-87cd-fd11a9a34cf0", "MzAzYTc5MGQtNjU3Ny00NWUzLWI0NzUtNzI0MzY1MmJlZjIx", ("profileId", "buildName", "dollarSpent")),
    # GameConfig("Sup_TEST",  "08869022-9bea-4f4d-8a87-cc62e1488bde", "NjRjMmVjNDgtYWNiMy00OTY4LWEyM2UtMzc3ZjdkNTI3Yzlm", ("profileId", "buildName", "dollarSpent")),
]
total_timer = common.Timer()
for game in gameConfigs:
    process_game(game)
print_group("Total time:", total_timer.formatedDuration())
