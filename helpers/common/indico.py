from urllib.parse import urljoin

import requests


class Indico:
    def __init__(self, config):
        self.base = config["url"]
        self.token = config["key"]

    def user_by_email(self, email):
        headers = {"Authorization": "Bearer " + self.token}
        data = {"email": email, "exact": "true"}

        r = requests.get(
            urljoin(self.base, "/user/search/"),
            headers=headers,
            params=data,
            allow_redirects=False,
        )
        if "location" in r.headers and "/login/" in r.headers["location"]:
            raise Exception("Your token has expired")

        data = r.json()

        if "error" in data:
            raise Exception("Error: " + data["error_description"])

        if data["total"] > 0:
            return data["users"][0]
        else:
            return None

    def format_user(self, user):
        return urljoin(self.base, "/user/{}/profile/".format(user["id"]))

    def anonymize(self, user_id):
        # TODO There is no API call to anonymize automatically. Either a manual task or we need to
        # implement this in a plugin until Indico has the feature released.
        raise Exception("Not yet implemented")
