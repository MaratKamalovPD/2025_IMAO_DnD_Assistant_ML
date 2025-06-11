import subprocess
import csv
import secrets
import string
import os

ALIAS = "local"
BUCKET = "2710"
POLICY_NAME = f"{BUCKET}-access"
USER_COUNT = 10

def generate_password(length=20):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    unsafe_chars = {'"', "'", '\\', '`', ' ', '$'}
    safe_alphabet = ''.join(c for c in alphabet if c not in unsafe_chars)
    return ''.join(secrets.choice(safe_alphabet) for _ in range(length))

def run_mc_command(args):
    try:
        result = subprocess.run(["mc"] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка: {' '.join(e.cmd)}\n{e.stderr.strip()}")
        return None

# Создание бакета (если не существует)
run_mc_command(["mb", f"{ALIAS}/{BUCKET}"])

# Создание политики JSON
policy_json = f'''
{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": [
        "arn:aws:s3:::{BUCKET}",
        "arn:aws:s3:::{BUCKET}/*"
      ]
    }}
  ]
}}
'''.strip()

with open("policy.json", "w") as f:
    f.write(policy_json)

# Создание политики (create вместо add)
run_mc_command(["admin", "policy", "create", ALIAS, POLICY_NAME, "policy.json"])

# Создание пользователей и прикрепление политики
user_data = []
for i in range(USER_COUNT):
    username = f"user{i}"
    password = generate_password()

    run_mc_command(["admin", "user", "add", ALIAS, username, password])
    run_mc_command(["admin", "policy", "attach", ALIAS, POLICY_NAME, "--user", username])

    user_data.append({"username": username, "password": password})

# Удаление временного файла
os.remove("policy.json")

# Сохранение пользователей в CSV
with open("minio_users.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["username", "password"])
    writer.writeheader()
    writer.writerows(user_data)

print("✅ Готово: пользователи созданы и логины сохранены в minio_users.csv")
