import requests


class Client:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in_url = None
        print("\n\033[1mWelcome to the news aggregator client!\033[0m")

    # Get list of agencies from directory service
    def get_agencies(self):
        # Fetch list of agencies from directory service
        print("\n\033[1;34mAttempting to retrieve list of agencies from directory service\033[0m")

        # Send get request to /api/directory endpoint of the directory service
        try:
            response = self.session.get('https://newssites.pythonanywhere.com/api/directory')
        except requests.exceptions.RequestException:
            print(f"\033[1;31m✘ Unable to connect to directory service\033[0m\n")
            return

        # Handle directory service unable to process request
        if response.status_code != 200:
            print(f"\033[1;31m✘ Failed to fetch agencies from directory service: (code {response.status_code}): "
                  f"{response.text}\033[0m\n")
            return

        # Handle no agencies returned
        if len(response.json()) == 0:
            print("\033[1;31m✘ No agencies found\033[0m\n")
            return

        # Parse response text into list of agencies
        agencies = response.json()
        print(f"\033[1;32m✔ {len(agencies)} agencies found \033[0m")

        return agencies

    # Retrieve agencies from directory service and list them
    def list_agencies(self):
        # Get list of agencies from directory service
        agencies = self.get_agencies()

        # Display list of agencies
        for agency in agencies:
            print(f"{agency['agency_name']} - {agency['url']} - {agency['agency_code']}")

        print("")

    # Log in to news service
    def login(self, url=None):
        # Ensure user is not already logged in
        if self.logged_in_url is not None:
            print("\033[1;31mError: Already logged in to a news service, please log out\033[0m")
            return

        # Ensure user has entered a login url
        if url is None or len(url) < 1:
            print("\033[1;31mError: No login url provided\033[0m")
            return

        # Strip trailing slash if present
        if url[-1] == "/":
            url = url[:-1]

        print(f"\n\033[1;34mAttempting to log in to news service @ {url}\033[0m")

        # Get username and password from user
        username = input("\033[34m?\033[0m Enter username > ")
        password = input("\033[34m?\033[0m Enter password > ")

        # Send post request to /api/login
        try:
            response = self.session.post(f'http://{url}/api/login', data={'username': username, 'password': password})
        except requests.exceptions.RequestException:
            print(f"\033[1;31m✘ Login failed: unable to connect to news service @ {url}\033[0m\n")
            return

        # Handle authentication failing
        if response.status_code != 200:
            print(f"\033[1;31m✘ Login failed (code {response.status_code}): {response.text}\033[0m\n")
            return

        # Finished, print success message & set url in global scope
        print("\033[1;32m✔ Login successful\033[0m\n")
        self.logged_in_url = url

    # Log out of news service
    def logout(self):
        # Ensure user is logged in
        if self.logged_in_url is None:
            print("\033[1;31mError: Not logged in to a news service\033[0m")
            return

        print(f"\n\033[1;34mAttempting to log out of news service @ {self.logged_in_url}\033[0m")

        # Send post request to /api/login
        try:
            response = self.session.post(f'http://{self.logged_in_url}/api/logout')
        except requests.exceptions.RequestException:
            print(f"\033[1;31m✘ Logout failed: unable to connect to news service @ {self.logged_in_url}\033[0m\n")
            return

        # Handle logout failing
        if response.status_code != 200:
            print(f"\033[1;31m✘ Logout failed (code {response.status_code}): {response.text}\033[0m\n")
            return

        # Finished, print success message
        print("\033[1;32m✔ Logout successful\033[0m\n")
        self.logged_in_url = None

    # Get news stories from news service(s)
    def get_stories(self, agency_id=None, category='*', region='*', date='*'):
        # Get list of agencies from directory service
        agencies = self.get_agencies()

        # If id parameter provided, filter list of agencies to only include the one with the matching id
        if agency_id is not None:
            print(f"\033[1;34mAttempting to retrieve stories from agency with id {agency_id}\033[0m")
            agencies = [agency for agency in agencies if agency["agency_code"] == agency_id]
        else:
            print(f"\033[1;34mAttempting to retrieve stories from all agencies\033[0m")

        # Ensure agency is found matching id switch
        if len(agencies) == 0:
            print("\033[1;31m✘ No agencies found matching id provided\033[0m\n")
            return

        # Get stories from each agency
        for agency in agencies:
            # Strip trailing slash if present
            if agency["url"][-1] == "/":
                agency["url"] = agency["url"][:-1]

            # Send get request to /api/stories endpoint of the news service
            try:
                response = self.session.get(url=f'{agency["url"]}/api/stories?story_cat={category}'
                                                f'&story_region={region}&story_date={date}',
                                            headers={'Content-Type': 'application/x-www-form-urlencoded'})
            except requests.exceptions.RequestException:
                print(f"\033[1;31m✘ Unable to connect to news service @ {agency['url']}\033[0m")
                continue

            # Handle news service unable to process request
            if response.status_code != 200:
                # Don't print response text if it is HTML not an error message
                if response.text.startswith("<!DOCTYPE html>") or response.text.startswith("<html>"):
                    error_msg = "API returned HTML but JSON expected"
                else:
                    error_msg = response.text
                print(f"\033[1;31m✘ Failed to fetch stories from news service @ {agency['url']}: "
                      f"(code {response.status_code}): {error_msg}\033[0m")
                continue

            # Handle news service return HTML ewhen status code is 200
            if response.text.startswith("<!DOCTYPE html>") or response.text.startswith("<html>"):
                print(f"\033[1;31m✘ Failed to fetch stories from news service @ {agency['url']}: "
                      f"API returned HTML but JSON expected")
                continue

            # Parse response text into list of stories
            try:
                payload = response.json()
                stories = payload['stories']
            except ValueError:
                print(f"\033[1;31m✘ Failed to fetch stories from news service @ {agency['url']}: invalid JSON response")
                continue
            except KeyError:
                print(f"\033[1;31m✘ Failed to fetch stories from news service @ {agency['url']}:"
                      f"invalid or missing keys in JSON response")
                continue

            # Notify user of number of stories found
            if len(stories) == 1:
                print(f"\033[1;32m✔ 1 story found from {agency['agency_name']} @ {agency['url']}\033[0m")
            else:
                print(f"\033[1;32m✔ {len(stories)} stories found from {agency['agency_name']} @ {agency['url']}\033[0m")

            # Display list of stories
            for story in stories:
                try:
                    print("----------------------------------\n"
                          f"Key: {story['key']}\nHeadline: {story['headline']}\nCategory: {story['story_cat']}\n"
                          f"Region: {story['story_region']}\nAuthor: {story['author']}\nDate: {story['story_date']}\n"
                          f"Details: {story['story_details']}")
                    if story == stories[-1]:
                        print("----------------------------------")
                except KeyError:
                    print(f"\033[1;31m↪ ✘ Failed to read stories: invalid or missing keys in JSON response")
                    break
            # End of loop through stories
        # End of loop through agencies

        # Finished, print success message
        "----------------------------------"
        print(f"\n\033[1;32m✔ Finished fetching stories from {len(agencies)} agencies\033[0m\n")

    # Post story to news service
    def post_story(self):
        # Ensure user is logged in
        if self.logged_in_url is None:
            print("\033[1;31mError: Not logged in to a news service\033[0m")
            return

        print(f"\n\033[1;34mAttempting to post a story to news service @ {self.logged_in_url}\033[0m")

        # Get required story details from user
        headline = input("\033[34m?\033[0m Enter headline > ")
        category = input("\033[34m?\033[0m Enter category > ")
        region = input("\033[34m?\033[0m Enter region > ")
        details = input("\033[34m?\033[0m Enter details > ")

        # Send post request to /api/stories
        try:
            response = self.session.post(url=f'http://{self.logged_in_url}/api/stories',
                                         json={'headline': headline, 'category': category, 'region': region,
                                               'details': details})
        except requests.exceptions.RequestException:
            print(f"\033[1;31m✘ Unable to connect to news service @ {self.logged_in_url}\033[0m\n")
            return

        # Handle post request failing
        if response.status_code != 201:
            print(f"\033[1;31m✘ Failed to post story (code {response.status_code}): {response.text}\033[0m\n")
            return

        # Finished, print success message
        print("\033[1;32m✔ Story posted successfully\033[0m\n")

    # Delete a news story from news service
    def delete_story(self, story_key=None):
        if self.logged_in_url is None:
            print("\033[1;31mError: Not logged in to a news service\033[0m")
            return

        # Ensure user has entered a story key
        if story_key is None or len(story_key) < 1:
            print("\033[1;31mError: No story key provided\033[0m")
            return

        print(f"\n\033[1;34mAttempting to delete story with key {story_key} from news service @ "
              f"{self.logged_in_url}\033[0m")

        # Send delete request to /api/stories/<story_id>
        try:
            response = self.session.delete(f'http://{self.logged_in_url}/api/stories/{story_key}')
        except requests.exceptions.RequestException:
            print(f"\033[1;31m✘ Unable to connect to news service @ {self.logged_in_url}\033[0m\n")
            return

        # Handle delete request failing
        if response.status_code != 200:
            print(f"\033[1;31m✘ Failed to delete story (code {response.status_code}): {response.text}\033[0m\n")
            return

        # Finished, print success message
        print("\033[1;32m✔ Story deleted successfully\033[0m\n")


def main():
    # Create new client instance
    client = Client()

    # Loop infinitely to accept user input & run commands until exit command is given
    while True:
        # Wait for user to input command & arguments
        input_parts = input("> ").split(" ")
        command = input_parts[0]
        args = input_parts[1:]

        # Run appropriate client method based on command
        if command == "exit":
            break
        elif command == "login":
            client.login(url=args[0])
        elif command == "logout":
            client.logout()
        elif command == "post":
            client.post_story()
        elif command == "delete":
            client.delete_story(story_key=args[0])
        elif command == "list":
            client.list_agencies()
        elif command == "news":
            switches = {}
            for arg in args:
                if "=" in arg:
                    key, value = arg.split("=")
                    switches[key] = value
            client.get_stories(**switches)
        else:
            print("\033[1;31mError: Invalid command\033[0m")


if __name__ == "__main__":
    main()
