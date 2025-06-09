import subprocess
import csv
import secrets
import string

ALIAS = "myminio"
BUCKET = "2710"
POLICY_NAME = "shared-bucket-2710-access"
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
        print(f"Ошибка: {' '.join(e.cmd)}\n{e.stderr}")
        return None

# Создание бакета (если нет)
run_mc_command(["mb", f"{ALIAS}/{BUCKET}"])

# Создание политики
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

run_mc_command(["admin", "policy", "add", ALIAS, POLICY_NAME, "policy.json"])

# Создание пользователей
user_data = []
for i in range(USER_COUNT):
    username = f"user{i}"
    password = generate_password()

    run_mc_command(["admin", "user", "add", ALIAS, username, password])
    run_mc_command(["admin", "policy", "set", ALIAS, POLICY_NAME, f"user={username}"])

    user_data.append({"username": username, "password": password})

# Сохранение в CSV
with open("minio_users.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["username", "password"])
    writer.writeheader()
    writer.writerows(user_data)

print("✅ Пользователи созданы, политика назначена, логины сохранены в minio_users.csv")
