from config import FORM_ID, SCOPES
from google.oauth2 import service_account
from googleapiclient.discovery import build
from lib.misc import get_today

fields = {
    "7d0c020d": "deadline",
    "7c56044a": "homework",
    "59f06f09": "subject",
    "75f1a49d": "additional_info",
}


class GoogleForms:
    _scopes: list
    __creds: str
    __form_id: str

    def __init__(self, scopes: list, creds_path: str, form_id: str) -> None:
        self._scopes = scopes
        self.__form_id = form_id
        self.__creds = service_account.Credentials.from_service_account_file(
            filename=creds_path
        )
        self.service = build("forms", "v1", credentials=self.__creds)

    def _get_form_responses(self) -> list:
        return (
            self.service.forms()
            .responses()
            .list(formId=self.__form_id)
            .execute()
            .get("responses")
        )

    def _get_latest_responses(self) -> list:
        today = get_today().date
        today = "2024-03-11"
        # TODO: fix to a current date
        todays_responses = [
            resp
            for resp in self._get_form_responses()
            if resp["lastSubmittedTime"].split("T")[0] == today
        ]
        return todays_responses

    def _parse_response(self, response: dict) -> dict | None:
        if not response.get("answers"):
            return
        response_fixed = {}
        for key in response.get("answers").keys():
            val = response.get("answers").get(key, dict())
            try:
                answer = val["textAnswers"]["answers"][0]["value"]
            except (KeyError, IndexError):
                answer = ""
            response_fixed[fields[key]] = answer
        return response_fixed

    def get_responces(self) -> list:
        responces = self._get_latest_responses()
        return [self._parse_response(resp) for resp in responces]


gf = GoogleForms(
    scopes=SCOPES, creds_path="./studentsbot-414221-88a1d65d3976.json", form_id=FORM_ID
)

from pprint import pprint

pprint(gf.get_responces())
