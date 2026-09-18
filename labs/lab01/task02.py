import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.student import *

users = {
    "risk_manager": {"role": "risk_analyst", "clearance": 4, "department": "Risk Management", "active": True},
    "business_analyst": {"role": "business_analyst", "clearance": 2, "department": "Business", "active": True},
    "legal_counsel": {"role": "legal", "clearance": 3, "department": "Legal", "active": True},
    "contractor_dev": {"role": "contractor", "clearance": 2, "department": "Contract", "active": True},
    "obsolete_system": {"role": "legacy_system", "clearance": 1, "department": "Legacy", "active": False},
}

resources = [("risk_registers", 4), ("business_requirements", 2), ("legal_documents", 3), ("contract_code", 2), ("governance_framework", 4), ("meeting_minutes", 1), ("regulatory_reports", 3), ("executive_dashboards", 4), ("project_specs", 2), ("public_statements", 1)]
security_levels = ("Public", "Internal Use", "Restricted", "Highly Restricted")
blocked_users = {"obsolete_system", "contract_expired", "legal_hold"}

width = max([len(x[0]) for x in resources])

print("Cписок ресурсів")
print("---------------")
for resource in resources:
    print(resource[0] + " " * (width-len(resource[0])), security_levels[resource[1]-1])

print("\n"*3+"Перевірка доступу користувачів")
counter = 1;
for username in users:
    userdata = users[username]
    for resource in resources:
        status = "ALLOW"
        if username not in users.keys():
            status = "DENY (User not found)" # as required by assignment. check every existing user if they exist in the database duh
        elif username in blocked_users:
            status = "DENY (User is blocked)"
        elif not userdata["active"]:
            status = "DENY (Account inactive)"
        elif userdata["clearance"] < resource[1]:
            status = "DENY (Insufficient clearance)"
        print(f"user={username} resource={resource[0]} -> {status}")
    counter+=1
