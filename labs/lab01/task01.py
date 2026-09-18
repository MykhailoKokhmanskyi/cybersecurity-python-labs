import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.student import *

passwords = ["APT@Detect10n", "simple", "Red@Team2023", "participant", "BLue@T3am", "common123", "Purple@T34m", "regular123", "Gr33n@Team", "normal123"]
criteria = {"min_length": 7, "require_digits": True, "require_upper": True, "require_special": True}
forbidden_passwords = {"simple", "participant", "common123", "regular123", "normal123", "test"}

width = max([len(x) for x in (passwords + ["Пароль"])])

print("Пароль" + " " * (width-6) + " | Вердикт")
print("-" * (width+15))

for i in range(3):
    password = passwords[random.randrange(0, len(passwords)-1)]
    print(password + " " * (width-len(password)), end=" | ")
    if len(password) < criteria["min_length"] or password in forbidden_passwords:
        print("Заборонений")
        continue
    
    hasupper = password.lower() != password
    hasspecial = False
    hasdigits = False

    digits = ["0","1","2","3","4","5","6","7","8","9"]
    for digit in digits:
        if digit in password:
            hasdigits = True
            break

    special = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "=", ",", ".", ";", ";", "/", "|", "\\"]
    for char in special:
        if char in password:
            hasspecial = True
            break
    
    score = hasupper + hasspecial + hasdigits

    match score:
        case 1:
            print("Слабкий")
        case 2:
            print("Середній")
        case 3:
            if(len(password) < criteria["min_length"]+4):
                print("Сильний")
            else:
                print("Дуже сильний")
