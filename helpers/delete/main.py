from ..common.discourse import CanDiscourseClient
from ..common.indico import Indico
from ..common.config import DISCOURSE_CONFIG, INDICO_CONFIG


def delete_by_email(email):
    # Discourse Instances
    for instancekey, data in DISCOURSE_CONFIG.items():
        discourse = CanDiscourseClient(instancekey, data)

        user = discourse.dataquery_gdpr_user(email)
        if user:
            discourse.anonymize(user["id"])

    # Indico Instances
    for instancekey, data in INDICO_CONFIG.items():
        indico = Indico(data)

        user = indico.user_by_email(email)
        if user:
            indico.anonymize(user["id"])
