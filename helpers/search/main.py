from ..common.discourse import CanDiscourseClient
from ..common.indico import Indico
from ..common.config import DISCOURSE_CONFIG, INDICO_CONFIG


def search_by_email(email):
    gdprdata = []

    # Discourse Instances
    for instancekey, data in DISCOURSE_CONFIG.items():
        discourse = CanDiscourseClient(instancekey, data)

        user = discourse.dataquery_gdpr_user(email)
        if user:
            gdprdata.append(
                {
                    "email": email,
                    "location": data["url"],
                    "profile_admin": discourse.format_user(user),
                }
            )

    # Indico Instances
    for instancekey, data in INDICO_CONFIG.items():
        indico = Indico(data)

        user = indico.user_by_email(email)
        if user:
            gdprdata.append(
                {
                    "email": email,
                    "location": data["url"],
                    "profile": indico.format_user(user),
                }
            )

    return gdprdata
