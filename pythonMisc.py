#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from Framework import common, jsonUtils, tkinterUtils, textParser

def get_all_packages_by_uid():
    # https://stackoverflow.com/questions/53634246/android-get-all-installed-packages-using-adb
    # .\adb.exe shell cmd package list packages -U
    path = """d:\Documents\_Arnaud\Climate\_BilanCarbone\GalaxyS9 - packages.txt"""
    lines = open(path, "r").readlines()
    res = { "-1": "System" }
    for line in lines:
        # Format is: package:com.mobeam.barcodeService uid:1000
        tokens = line.strip().split(" ")
        res[tokens[1][4:]] = tokens[0].replace("package:", "")
    return res


def get_date(time_stamp):
    readable = datetime.datetime.fromtimestamp(time_stamp).isoformat()
    return readable


def process():
    # DOCUMENTATION:
    # adb shell dumpsys netstats detail full > data_usage.txt
    # https://developer.android.com/studio/command-line/dumpsys
    # https://www.cnblogs.com/pengdonglin137/articles/5411601.html
    path = """d:\Documents\_Arnaud\Climate\_BilanCarbone\GalaxyS9 - data_usage.txt"""
    text = open(path, 'r').read()
    separators = [
        "Active interfaces:",
        "Active UID interfaces:",
        "Dev stats:",
        "Xt stats:",
        "UID stats:",
        "UID tag stats:",
    ]
    categories = textParser.split_texts(text, *separators)
    for i, cat in enumerate(categories):
        # Remove title line
        cat = cat.replace("\r\n", "\n").split("\n")
        for j in reversed((range(len(cat)))):
            line = cat[j].strip()
            if line == "":  cat.pop(j)
            else:           cat[j] = line
        categories[i] = cat

    packages_uids = get_all_packages_by_uid()

    def parse_category(cat_lines):
        res = {}
        i = 3
        total = 0
        while i < len(cat_lines):
            line = cat_lines[i]
            # Parse "ident=[{type=MOBILE, subType=COMBINED, subscriberId=208103..., metered=false}] uid=-1 set=ALL tag=0x0"
            uid = line[line.find("uid="):].split(" ")[0].replace("uid=", "")
            if not uid in packages_uids:
                packages_uids[uid] = "UNKNOWN"
            package = packages_uids[uid]

            # Skip "NetworkStatsHistory: bucketDuration=3600"
            i += 2

            # Parse block until next "ident"
            package_total = 0 if package not in res else res[package]
            while i < len(cat_lines):
                line = cat_lines[i]
                if line.startswith("ident"):
                    break

                i += 1

                # Line format: st=1648458000 rb=1920 rp=5 tb=3187 tp=5 op=0
                tokens = line.split(" ")
                print(get_date(int(tokens[0][3:])))
                received_bytes = float(tokens[1][3:]) / 1024 / 1024
                package_total += received_bytes
                total += received_bytes
            res[package] = package_total

        # Print results
        keys = [k for k in res]
        keys.sort(key=lambda x: res[x])
        keys.reverse()
        print("{}\t{:.2f}".format(cat_lines[0], total))
        for k in keys:
            print("\t{}\t{:.2f}".format(k, res[k]))
        return res

    parse_category(categories[2])
    parse_category(categories[3])
    parse_category(categories[4])
    parse_category(categories[5])

    print("END")



process()