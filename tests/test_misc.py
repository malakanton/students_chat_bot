import pytest
from app.lib.misc import prep_markdown, get_today, valid_schedule_format
import datetime as dt
import os


def test_prep_mkdwn():
    assert prep_markdown('.') == '\\.', 'test prep markdown failed'


def test_today():
    assert get_today().date == dt.datetime.now().date(), 'get today failed'


def test_valid_schedule_format():
    names = [name for name in os.listdir('./temp') if name.startswith('Очно')]
    for name in names:
        assert valid_schedule_format(name)
