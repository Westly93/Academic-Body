import json
usernames = ['Westonmf', 'mukute', 'chaibva']
emails = ['westonmufudza@gmail.com',
          'mukute@staff.msu.ac.zw', 'chaibvan@staff.msu.ac.zw']

passwords = ['testing321', 'testing321#', 'testing123']

credentials = {"usernames": {}}

for index in range(len(emails)):
    credentials["usernames"][usernames[index][0]] = {
        "name": emails[index][0],
        "password": passwords[index][0]
    }
prettified_creds = json.dumps(credentials, indent=4)
print(prettified_creds)
