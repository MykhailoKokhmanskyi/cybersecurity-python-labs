import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import *

width = max([len(x[0]) for x in resources])

print("Cписок ресурсів")
print("---------------")
for resource in resources:
    print(
        resource[0] + " " * (width - len(resource[0])), security_levels[resource[1] - 1]
    )

print("\n" * 3 + "Перевірка доступу користувачів")
counter = 1
for username in users:
    userdata = users[username]
    for resource in resources:
        status = "ALLOW"
        if username not in users:
            status = "DENY (User not found)"  # as required by assignment. check every existing user if they exist in the database duh
        elif username in blocked_users:
            status = "DENY (User is blocked)"
        elif not userdata["active"]:
            status = "DENY (Account inactive)"
        elif userdata["clearance"] < resource[1]:
            status = "DENY (Insufficient clearance)"
        print(f"user={username} resource={resource[0]} -> {status}")
    counter += 1
