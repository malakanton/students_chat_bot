import re
import pytest
from app.lib.logs_report import parce_line


@pytest.fixture()
def log_line() -> str:
    return '2024-03-24T01:27:07.296997+0300|INFO|handlers.users.schedule:change_week:83|user_id: 1234567' \
           ' chat_id: 1234567 chat_type: private command: schedule:12:FORW message:'


def test_line_parser(log_line: str) -> None:
    log_items = parce_line(log_line)
    for item in ['timestamp', 'user_id', 'command', 'message', 'chat_id', 'chat_type']:
        assert item in log_items.keys()
    assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', log_items.get('timestamp'))
