import pandas as pd
import pdfplumber
import datetime as dt
import re
import logging


def plumb_pdf(
        filename: str
) -> tuple:
    with pdfplumber.open(filename) as f:
        table = f.pages[0].extract_table(
            table_settings={
                "text_y_tolerance": 0.1,
                "intersection_y_tolerance": 1,
                "intersection_x_tolerance": 3,
                "snap_y_tolerance": 0.5
            }
        )
        text = f.pages[0].extract_text(
            keep_blank_chars=True,
            y_tolerance=0.5,
            x_tolerance=0.5
        )

    dates = re.findall(r'\d{2}(?:_|\.|\s)\d{2}', filename)
    dates = [date.replace('_', '.') for date in dates]
    if len(dates) != 2:
        search_res = re.search('[сc]\s?\d{1,2}\.\d{1,2}\.?\s?(по|-)\s?\d{1,2}\.\d{1,2}', text).group(0)
        search_res = search_res.split()[1:]
        dates = [s for s in search_res if 'по' not in s and '-' not in s]
    df = pd.DataFrame(table[1:], columns=table[0])
    return df, dates


def get_monday(
        dates: list
) -> dt.datetime:
    return dt.datetime(
        dt.datetime.now().year,
        int(dates[0].split('.')[1]),
        int(dates[0].split('.')[0])
    )


def process_empty_cols(columns):
    if not columns[0]:
        columns[0] = 'day'
    if not columns[1]:
        columns[1] = 'hours'
    return columns


def process_columns(
        df: pd.DataFrame
) -> pd.DataFrame:
    df = df.copy()
    df = df.rename({
        'ДНИ': 'day',
        'ЧАСЫ': 'hours',
        'ГРУППА': 'lesson_num',
    }, axis=1)
    columns = list(df.columns).copy()
    columns = process_empty_cols(columns)
    for i, col in enumerate(columns):
        if not col:
            columns[i] = f'empty_{i}'
        elif 'ауд' in col:
            group = columns[i-1]
            if 'empty' in group:
                group = columns[i-2]
            columns[i] = group + '_loc'
    df.columns = columns
    empty_columns = [col for col in df.columns if 'empty' in col]
    df.drop(empty_columns, axis=1, inplace=True)
    return df


def days_of_week(
        text: str
) -> str:
    if not text:
        return text
    text = text.replace('\n', '')
    text = text[::-1]
    return text.lower().capitalize()


def get_dates(
        days: list,
        dates: list
) -> list:
    monday_date = get_monday(dates)
    curr_day, curr_date = days[0], monday_date
    dates_list = []
    for day in days:
        if day != curr_day:
            curr_date += dt.timedelta(days=1)
            curr_day = day
        dates_list.append(curr_date)
    return dates_list


def merge_dt(
        date: dt.datetime,
        time: str,
        start=True
):
    time_items = time.split('-')
    time = time_items[1]
    if start:
        time = time_items[0]
    return dt.datetime.combine(
        date.date(),
        dt.datetime.strptime(time, '%H.%M').time()
    )


def get_teacher(
        text: str
) -> str:
    text = text.replace('\n', ' ')
    pattern = r'([А-Я]{1}[а-я]*)?(\-[А-Я]{1}[а-я]*)? [А-Я]\.[А-Я]\.'
    try:
        return re.search(pattern, text).group(0)
    except:
        return ''


def get_subj_code(
        text: str
) -> str:
    text = text.replace('\n', ' ')
    code_pattern = r'^[А-Я]{1,5}\s?\d{0,2}\.?\d{1,3}\.?\d{0,2}'
    try:
        return re.search(code_pattern, text).group(0)
    except:
        return ''


def get_subj(
        text: str
) -> str:
    teacher_pattern = r'[\(]?([А-Я]{1}[а-я]*)?(\-[А-Я]{1}[а-я]*)? [А-Я]\.[А-Я]\.[\)]?'
    code_pattern = r'^[А-Я]{1,5}\s?\d{0,2}\.?\d{1,3}\.?\d{0,2}'
    text = text.replace('\n', ' ')
    text = re.sub(teacher_pattern, '', text)
    text = re.sub(code_pattern, '', text)
    return text.strip()


def clean_loc(text:str) -> str:
    if ' ' in text:
        text = text.replace(' ', '')
    if '\n' in text:
        text = text.replace('\n', '')
    return text


def process_df(
        df: pd.DataFrame,
        dates: list
) -> pd.DataFrame:
    df = df.copy()
    if df.iloc[0, 0] == 'НЕДЕЛИ':
        df.drop(0, inplace=True)
        df.reset_index(inplace=True, drop=True)
    if not df.iloc[0, 0]:
        df.drop(0, inplace=True)
        df.reset_index(inplace=True, drop=True)
    if not df.iloc[0, 0]:
        df.drop(0, inplace=True)
        df.reset_index(inplace=True, drop=True)
    df = process_columns(df)
    df['day'] = df.day.map(days_of_week).ffill()
    df['date'] = get_dates(list(df.day), dates)
    df['start'] = df[['date', 'hours']].apply(lambda x: merge_dt(x.date, x.hours), axis=1)
    df['end'] = df[['date', 'hours']].apply(lambda x: merge_dt(x.date, x.hours, start=False), axis=1)
    return df


def filter_df(
        df: pd.DataFrame,
        group: str
) -> pd.DataFrame:
    common_columns = [
        'day',
        'lesson_num',
        'start',
        'end'
    ]
    group_columns = [col for col in df.columns if group in col]
    filtered_df = df[common_columns + group_columns].copy()
    filtered_df.columns = common_columns + ['subj', 'loc']
    filtered_df.fillna('', inplace=True)
    filtered_df['loc'] = filtered_df['loc'].map(clean_loc)
    filtered_df['teacher'] = filtered_df.subj.map(get_teacher)
    filtered_df['subj_code'] = filtered_df.subj.map(get_subj_code)
    filtered_df['subj'] = filtered_df.subj.map(get_subj)
    return filtered_df


def get_schedule(
        filename: str
) -> pd.DataFrame:
    logging.info('start schedule parsing')
    df_raw, dates = plumb_pdf(filename)
    logging.info(f"schedule dates: {dates}")
    logging.info(str(df_raw.head()))
    df = process_df(df_raw, dates)
    logging.info(f'processed df: {df.head()}')
    week_num = get_monday(dates).isocalendar()[1]
    return df, week_num
