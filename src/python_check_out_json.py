# Python program to read
# json file


import json

# Opening JSON file
f = open("aw-buckets-export.json")

# returns JSON object as
# a dictionary
data = json.load(f)

# Iterating through the json
# print(data)
# list
for k, i in data["buckets"]["aw-stopwatch"].items():
    print(i)
    print(k)

# Closing file
f.close()
