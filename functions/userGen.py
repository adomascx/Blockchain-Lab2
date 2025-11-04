import json
import random
from functions.hash import HashFunction

def userGeneration():
    users = []
    for i in range(1000):
        users.append({
            "name": "bob" + str(i+1),
            "public_key": f"{HashFunction(i+1)}",
            "balance": random.randint(100, 1000000),
        })
    return users