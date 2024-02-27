import pickle
from pathlib import Path
import streamlit_authenticator as stauth


names = ['Westonmf', 'mukute', 'chaibva']
usernames = ['westonmufudza@gmail.com',
             'mukute@staff.msu.ac.zw', 'chaibvan@staff.msu.ac.zw']

passwords = ['testing321', 'testing321#', 'testing123']
hashed_passwords = stauth.Hasher(passwords).generate()
file_path = Path(__file__).parent / 'hashed_pw.pkl'

with file_path.open('wb') as file:
    pickle.dump(hashed_passwords, file)
