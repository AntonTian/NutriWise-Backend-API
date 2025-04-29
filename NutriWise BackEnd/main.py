import firebase_admin as fa
from firebase_admin import credentials, firestore, auth
import requests
from dotenv import load_dotenv
import os

cred = credentials.Certificate("ServiceAccountKey.json")
fa.initialize_app(cred)

db = firestore.client()

load_dotenv(dotenv_path=".idea/.env")

api_key = os.getenv('API_KEY')

def register_user(name, email, password):
    try:
        # 1. Create user in Firebase Auth
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        print(f'Successfully created user: {user.uid}')

        # 2. Create user document in Firestore
        db.collection('users').document(user.uid).set({
            'name': name,
            'email': email,
            'uid': user.uid,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        print(f'Successfully added user to Firestore: {user.uid}')
        return user
    except Exception as e:
        print(f'Error creating user: {e}')
        return None

def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        id_token = data['idToken']
        print("Successfully logged in!")
        print(f"ID Token: {id_token}")

        #fetch user Firestore document
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        user_doc = db.collection('users').document(uid).get()
        if user_doc.exists:
            print("User Firestore Data:", user_doc.to_dict())
            return {
                "idToken": id_token,
                "userData": user_doc.to_dict()
            }
        else:
            print("No user document found!")
            return {
                "idToken": id_token,
                "userData": None
            }
    else:
        print("Failed to log in:", response.json())
        return None

if __name__ == "__main__":
    print("Welcome!")
    while True:
        action = input("register or login? ").lower()

        if action == 'register':
            print("Register New User")
            name = input("Enter your name: ")
            # Validate Email
            while True:
                email = input("Enter your email (must be @gmail.com): ").strip()
                if email.endswith("@gmail.com"):
                    break
                else:
                    print("Invalid email. Please use a @gmail.com email address.")

            #Validate password
            while True:
                password = input("Enter your password: ")
                if len(password) < 8:
                    print("Password must be at least 8 characters long. Please try again.")
                elif len(password) >= 8:
                    break

            register_user(name, email, password)

        elif action == 'login':
            print("Login User")
            email = input("Enter your email: ")
            password = input("Enter your password: ")

            login_user(email, password)

        else:
            print("type register or login only")