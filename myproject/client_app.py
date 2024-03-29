import requests
from getpass import getpass

# Base URL of your Django development server
BASE_URL = 'http://127.0.0.1:8000'

# Create a session object to persist the login state and reuse HTTP connection
session = requests.Session()

def login():
    username = input("Enter username: ")
    password = getpass("Enter password: ")  # Use getpass to hide password input
    try:
        # Send login request to the server
        response = session.post(f"{BASE_URL}/api/login/", json={'username': username, 'password': password})

        # Debugging prints
        print("Request sent to:", response.url)
        print("Status code:", response.status_code)
        print("Response body:", response.text)

        # Check if login was successful
        if response.status_code == 200:
            print("Login successful.")
        else:
            print(f"Login failed with status code {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def post_story():
    if not session.cookies.get('sessionid'):
        print("You must be logged in to post a story.")
        return

    headline = input("Headline: ")
    category = input("Category (pol, art, tech, trivia): ")
    region = input("Region (uk, eu, w): ")
    details = input("Details: ")

    story_data = {
        'headline': headline,
        'category': category,
        'region': region,
        'details': details
    }
    response = session.post(f"{BASE_URL}/api/stories/", json=story_data)
    if response.ok:
        print("Story posted successfully.")
    else:
        print("Failed to post story.")

def get_stories():
    category = input("Category (pol, art, tech, trivia) or '*' for all: ")
    region = input("Region (uk, eu, w) or '*' for all: ")
    date = input("Date (YYYY-MM-DD) or '*' for all: ")

    params = {'story_cat': category, 'story_region': region, 'story_date': date}
    response = session.get(f"{BASE_URL}/api/stories/", params=params)
    if response.ok:
        stories = response.json()
        for story in stories['stories']:
            print(story)
    else:
        print("Failed to retrieve stories.")

def logout():
    response = session.post(f"{BASE_URL}/api/logout/")
    if response.ok:
        print("Logged out successfully.")
    else:
        print("Failed to log out.")

def delete_story():
    if not session.cookies.get('sessionid'):
        print("You must be logged in to delete a story.")
        return

    story_id = input("Story ID to delete: ")
    response = session.delete(f"{BASE_URL}/api/stories/{story_id}/")
    if response.ok:
        print("Story deleted successfully.")
    else:
        print("Failed to delete story.")

def main():
    while True:
        command = input("Enter command (login, post, get, delete, logout, quit): ").strip().lower()
        if command == 'login':
            login()
        elif command == 'post':
            post_story()
        elif command == 'get':
            get_stories()
        elif command == 'delete':
            delete_story()
        elif command == 'logout':
            logout()
        elif command == 'quit':
            break
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
