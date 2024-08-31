import os
import requests
from urllib.parse import urljoin
from loguru import logger
from requests import Session
from requests.exceptions import HTTPError, JSONDecodeError
from typing import Optional, Dict, List, Union
from lib.models.users import Teacher
from lib.models.group import Group, Groups

GET = "GET"
POST = "POST"
OK = 'OK'
ERROR = 'Error'
class ScheduleClient:
    __host: str
    __port: str

    def __init__(self, host: str, port: str):
        self.url = f'http://{host}:{port}'
        self._session = Session()
        self.check_status()

    def check_status(self):
        r = self._session.get(self.url)
        if r.text != 'OK':
            raise Exception(f'failed to init schedule client: {r.text}')
        logger.info(f'schedule service responce {r.text}')

    def request(self, method: str, handler: str, body: Dict = None) -> Optional:
        try:
            resp = self._session.request(
                method,
                urljoin(self.url, handler),
                json=body)
            resp.raise_for_status()
            return resp.json()

        except JSONDecodeError as e:
            logger.info(f'Failed to decode json: {e}')

        except HTTPError as e:
            logger.error(f'Error occured: {e}')

    def get_teachers(self, id: int = -1):

        if id < 0:
            id = 'all'
        resp = self.request(GET, f'teachers/{id}')
        if resp.get('status', '') == OK:
            if id == 'all':
                return [Teacher(**item) for item in resp.get('teachers')]
            return Teacher(**resp.get('teacher'))
        return resp

    def register_teacher(self, code: str, tg_id: int):
        body = {
            'tg_id': tg_id,
            'code': code,
        }
        resp = self.request(POST, f'teachers/register', body=body)
        status = resp.get('status', '')

        if status == OK:
            return Teacher(**resp.get('teacher'))

        elif status == ERROR:
            return resp.get('error', '')

        return resp

    def get_teacher_daily_lessons(self, teacher_id: int, date: str) -> Dict:
        resp = self.request(GET, f'lessons/teacher/{teacher_id}/daily/{date}')
        return resp

    def get_teacher_weekly_lessons(self, teacher_id: int, week_num: int) -> Dict:
        resp = self.request(GET, f'lessons/teacher/{teacher_id}/weekly/{week_num}')
        return resp

    def get_group_daily_lessons(self, group_id: int, date: str) -> Dict:
        resp = self.request(GET, f'lessons/group/{group_id}/daily/{date}')
        return resp

    def get_group_weekly_lessons(self, group_id: int, week_num: int) -> Dict:
        resp = self.request(GET, f'lessons/group/{group_id}/weekly/{week_num}')
        return resp

    def get_groups(self) -> Union[Groups, str]:
        resp = self.request(GET, f'groups/0')
        status = resp.get('status', '')

        if status == OK:
            return Groups(groups=[Group(**item) for item in resp.get('groups')])

        elif status == ERROR:
            return resp.get('error', '')

        return resp


# client = ScheduleClient('0.0.0.0', '8080')
#
# print(client.get_groups())
#
# print(client.get_teachers(3))
#
# # print(client.register_teacher('DpNzKnio', 12345))
#
# print(client.get_teacher_daily_lessons(17, '2024-06-04'))
#
# print(client.get_group_daily_lessons(6, '2024-06-04'))