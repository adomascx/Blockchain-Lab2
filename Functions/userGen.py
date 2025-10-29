import json
import random

def userGeneration():
    users = []
    for i in range(1000):
        users.append({
            "name": "bob" + str(i+1),
            "public_key": f"{i+1}",
            "balance": random.randint(100, 1000000),
        })
    return users

with open("users.json", "w", encoding="utf-8") as f:
    json.dump({"users": userGeneration()}, f, indent=2)