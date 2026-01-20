import hashlib
ids = {
    'user': 'user',
    'pw_user': 'user2685',
    'admin': 'admin',
    'pw_admin': 'admin205'
}

with open('hashes.txt', 'w') as f:
    for k, v in ids.items():
        h = hashlib.sha256(v.encode()).hexdigest()
        f.write(f'{k}:{h}\n')
