import sys
import os
import hashlib
import json
import functools
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.student import *

os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"), exist_ok=True)

SALT = "0" * (5-len(str(VARIANT_NUMBER))) + str(VARIANT_NUMBER)
MIN_PASSWORD_LENGTH = 12
users_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/users.csv")

users_db = None

users_to_register = (
    ("admin", "securePassword"),
    ("user1", "user1user1user1"),
    ("user2", "quertyqwertyqwerty"),
    ("user3", "123451234512345"),
    ("user4", "123451234512345"),
    ("user5", "qwertyqwertqwerty"),
    ("user6", "1912197519121975"),
    ("user7", "0918202609182026"),
    ("user8", "TryH@ckM3TryH@ckM3"),
    ("user0", "123123123123123123"),
)

class ValidationError(Exception):
    pass

def log_event(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "data", "log.json")
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            res = func(*args, **kwargs)
            result_status = "success" if res else "failure"
        except Exception as e:
            result_status = "failure"
            res = None

        user = kwargs.get("user") or (args[0] if args else "unknown")
        
        log_entry = {
            "event": "login",
            "user": str(user),
            "result": result_status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "args": list(args),
            "kwargs": kwargs
        }
        
        logs = []
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = [logs]
            except (json.JSONDecodeError, OSError):
                logs = []
        
        logs.append(log_entry)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
            
        return res
        
    return wrapper

def validate_blake2b(password: str, expected_hex_hash: str, salt: str = "00000") -> bool:
    if not password or not salt:
        return False
        
    hasher = hashlib.blake2b(salt=salt.encode("utf-8"))
    hasher.update(password.encode("utf-8"))
    computed_hex_hash = hasher.hexdigest()
    return computed_hex_hash.strip() == expected_hex_hash.strip()

def generate_hash(password: str, salt: str = "00000") -> str:
    if password == None or password == "" or salt == None or salt == "":
        raise ValueError()
    
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError()
    
    hasher = hashlib.blake2b(salt=salt.encode("utf-8"))
    hasher.update(password.encode("utf-8"))
    return hasher.hexdigest()

def create_user(username, password):
    hashed_password = generate_hash(password, SALT)
    return (username, hashed_password)

def create_users(users_list):
    with open(users_file_path, "w+") as usersFile:
        for user in users_list:
            created_user = create_user(user[0], user[1])
            usersFile.write(f"{created_user[0]},{created_user[1]}\n")

@log_event
def login(username: str, password: str) -> bool:
    if username == "" or username is None or password == "" or password is None or users_db is None:
        raise ValueError()

    found = False
    for i, user in enumerate(users_db):
        if user[0] == username:
            uid = i
            found = True
            break
    if not found:
        return False

    user = users_db[uid]
    try:   
        return validate_blake2b(password, user[1], SALT)
    except:
        return False

def main():
    global users_db
    create_users(users_to_register)
    with open(users_file_path, "r") as usersFile:
        users_db_raw = usersFile.readlines()
        users_db = ()
        for user in users_db_raw:
            split = user.split(",")
            users_db += tuple([tuple([split[0], split[1][:-1].strip()])])
        width = max([len(u[0]) for u in (users_db + tuple([tuple(["Ім'я користувача", ""])]))])
        print("Ім'я користувача | Хеш паролю")
        print("-" * (width + len(users_db[0][1]) + 3))
        for user in users_db:
            print(user[0] + " " * (width-len(user[0])) + " | " + user[1])

        login("admin", "securePassword")
        login("admin", "wrongPassword")
        login("user1", "user1user1user1")
        login("user1", "wrong")

if __name__ == "__main__":
    main()
