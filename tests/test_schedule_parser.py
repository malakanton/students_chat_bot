import os
import re
import pytest
import pandas as pd
from app.loader import db, gc
from app.lib.schedule_parser import ScheduleParser, ScheduleFilter
from app.lib.schedule_uploader import ScheduleUploader


def get_schedule_files() -> list:
    path = './temp'
    return [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.pdf')]


@pytest.fixture(params=get_schedule_files())
def schedule_parser(request) -> ScheduleParser:
    filename = request.param
    print(f'Test ScheduleParser initialization for {filename}')
    sp = ScheduleParser(filename)
    return sp


def test_schedule_parser_dates(schedule_parser: ScheduleParser) -> None:
    assert len(schedule_parser.dates) == 2
    assert re.match(r'\d{1,2}.{2}', schedule_parser.dates[0])
    assert re.match(r'\d{1,2}.{2}', schedule_parser.dates[1])


def test_schedule_parser_weeknum(schedule_parser: ScheduleParser) -> None:
    assert type(schedule_parser.week_num) == int


@pytest.fixture()
def schedule_parser_dataframe(schedule_parser) -> ScheduleParser:
    schedule_parser.get_schedule()
    return schedule_parser


def test_schedule_parser_dataframe_extraction(schedule_parser_dataframe: ScheduleParser) -> None:
    assert isinstance(schedule_parser_dataframe.get_schedule(), pd.DataFrame)


@pytest.fixture(params=['day', 'hours', 'lesson_num'])
def column(request) -> None:
    return request.param


def test_schedule_parser_columns(schedule_parser_dataframe: ScheduleParser, column: str) -> None:
    assert column in schedule_parser_dataframe.df.columns


@pytest.fixture()
def groups() -> list:
    groups = db.get_groups()
    return groups


@pytest.fixture()
def schedule_filter(schedule_parser_dataframe: ScheduleParser, groups: list) -> ScheduleFilter:
    df = schedule_parser_dataframe.df
    sf = ScheduleFilter(df, groups)
    return sf


@pytest.fixture()
def schedule_filter_ready(schedule_filter: ScheduleFilter) -> ScheduleFilter:
    schedule_filter.extract_groups_schedules()
    return schedule_filter


def test_schedule_filter(schedule_filter: ScheduleFilter) -> None:
    assert isinstance(schedule_filter.schedules, dict)


def test_schedule_filter_ready(schedule_filter_ready: ScheduleFilter) -> None:
    for sch in schedule_filter_ready.schedules.values():
        assert isinstance(sch, pd.DataFrame)


def test_schedule_uploader() -> None:
    ScheduleUploader(5, gc)
