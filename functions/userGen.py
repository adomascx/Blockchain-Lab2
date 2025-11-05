import random
from functions.hash import HashFunction

USERS_COUNT = 1000

def userGeneration():
    users = []
    for i in range(USERS_COUNT):
        users.append({
            "name": "bob" + str(i+1),
            "public_key": f"{HashFunction(str(i+1))}",
            "balance": random.randint(100, 1000000),
        })
    return users