import json
from urllib.parse import urljoin

from pydiscourse import DiscourseClient
from pydiscourse.exceptions import DiscourseClientError


class CanDiscourseClient(DiscourseClient):
    def __init__(self, name, config):
        self.name = name
        super().__init__(
            config["url"], api_username=config["username"], api_key=config["key"]
        )
        self.config = config

    def anonymize(self, user_id):
        return self._put(f"/admin/users/{user_id}/anonymize.json")

    def dataquery_gdpr_user(self, email):
        fallback = True
        if "dataquery_gdpr_id" in self.config:
            fallback = False
            dqid = self.config["dataquery_gdpr_id"]
            try:
                resp = self._post(
                    f"/admin/plugins/explorer/queries/{dqid}/run",
                    params=json.dumps({"email": email}),
                )
                if not resp["success"]:
                    raise Exception("Data query failed: " + str(resp))

                if len(resp["rows"]) == 0:
                    return None

                uid, username, email = resp["rows"][0]
                return {"id": uid, "username": username, "email": email}
            except DiscourseClientError as e:
                if e.response.status_code == 404:
                    print(
                        f"Warning: {self.name} is configured for dataquery but the endpoint is 404"
                    )
                    fallback = True

        if fallback:
            data = self.user_by_email(email)
            if len(data) == 0:
                return None

            return data[0]

    def format_user(self, user):
        return urljoin(
            self.host, "/admin/users/{}/{}".format(user["id"], user["username"])
        )
