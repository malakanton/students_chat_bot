import datetime as dt
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import SCOPES, CREDS_PATH
import pprint


class GoogleCalendar:
    _scopes: list
    __creds: str

    def __init__(
            self,
            scopes: list = SCOPES,
            creds_path: str = CREDS_PATH
    ) -> None:
        self._scopes = scopes
        self.__creds = service_account.Credentials.from_service_account_file(
            filename=creds_path
        )
        self.service = build('calendar', 'v3', credentials=self.__creds)

    def _get_calendars(self) -> list:
        return self.service.calendarList().list().execute()['items']

    def _add_calendar(self, calendar_id) -> dict:
        calendar_list_entry = {
            'id': calendar_id
        }
        return self.service.calendarList().insert(body=calendar_list_entry).execute()

    def _get_events_from_list(
            self,
            schedule: list
    ) -> list:
        events = []
        for lesson in schedule:
            if lesson['subj'] != '':
                event = self._create_calendar_json(
                    lesson['subj'],
                    lesson['loc'],
                    lesson['start'],
                    lesson['end'])
                events.append(event)
        return events

    def _google_dt(self, datetime) -> str:
        return datetime.to_pydatetime().strftime('%Y-%m-%dT%H:%M:%S+03:00')

    def _create_calendar_json(
            self,
            subj: str,
            loc: str,
            start: str,
            end: str
    ) -> dict:
        event = {
            'summary': subj,
            'location': loc,
            'description': '',
            'start': {
                'dateTime': self._google_dt(start),
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': self._google_dt(end),
                'timeZone': 'Europe/Moscow',
            },
            'recurrence': [],
            'attendees': [],
            'reminders': {},
        }
        return event

    def _get_calendar_id(
            self,
            group_name: str
    ) -> str:
        for calendar in self._get_calendars():
            if calendar.get('summary') == group_name:
                return calendar.get('id')
        return ''

    async def upload_schedule(
            self,
            schedule: list,
            group_name: str,
            calendar_id: str = ''
    ) -> list:
        events = self._get_events_from_list(schedule)
        links = []
        if not calendar_id:
            calendar_id = self._get_calendar_id(group_name)
        if not calendar_id:
            return links
        for event in events:
            event_upl = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            links.append(
                event_upl.get('htmlLink')
            )
        return links

    async def update_schedule(
            self,
            schedule: list,
            group_name: str
    ):
        dates = [
            self._google_dt(lesson['start'])[:10]
            for lesson in schedule
        ]
        mon, sat = min(dates), max(dates)
        calendar_id = self._get_calendar_id(group_name)
        calendar_events = self.service.events().list(
            calendarId=calendar_id,
            pageToken=None
        ).execute()['items']
        for event in calendar_events:
            if mon <= event['start']['dateTime'][:10] <= sat:
                self.service.events().delete(
                    calendarId=calendar_id,
                    eventId=event['id']
                ).execute()
        await self.upload_schedule(schedule, group_name, calendar_id)
