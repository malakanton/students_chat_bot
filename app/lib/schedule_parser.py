import pandas as pd
import pdfplumber
import datetime as dt
import re
import logging
from lib.models import Group


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
    dates = get_schedule_dates(filename, text)
    df = pd.DataFrame(table[1:], columns=table[0])
    return df, dates


def get_schedule_dates(
        filename: str,
        text: str
) -> tuple:
    dates = re.findall(r'\d{1,2}(?:_|\.|\s)\d{1,2}', filename)
    dates = [date.replace('_', '.') for date in dates]
    if len(dates) != 2:
        search_res = re.search('[сc]\s?\d{1,2}\.\d{1,2}\.?\s?(по|-)\s?\d{1,2}\.\d{1,2}', text).group(0)
        search_res = search_res.split()[1:]
        dates = [s for s in search_res if 'по' not in s and '-' not in s]
    return tuple(dates)


def get_monday(
        dates: tuple
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
    return text.capitalize()


def get_dates(
        days: list,
        dates: tuple
) -> list:
    curr_day, curr_date = days[0], get_monday(dates)
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
        dt.datetime.strptime(time.strip(), '%H.%M').time()
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
    except AttributeError:
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


def clean_text(text: str, loc=False) -> str:
    separators = ['\n', '(', ')']
    if loc:
        separators.append(' ')
    for sep in separators:
        text = text.replace(sep, '')
    return text


def process_df(
        df: pd.DataFrame,
        dates: tuple
) -> pd.DataFrame:
    df = df.copy()
    while (
            df.iloc[0, 0] == 'НЕДЕЛИ' or
            not df.iloc[0, 0]
    ):
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
    filtered_df['loc'] = filtered_df['loc'].map(lambda x: clean_text(x, loc=True))
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


class ScheduleParser:
    filename: str
    dates: tuple[str]
    df: pd.DataFrame
    week_num: int
    _dates_filename_pattern: re.Pattern
    _dates_text_pattern: re.Pattern

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.df = pd.DataFrame()
        self.dates = self._extract_dates()
        self.week_num = self._get_monday().isocalendar()[1]
        self._dates_filename_pattern = re.compile(r'\d{1,2}(?:_|\.|\s)\d{1,2}')
        self._dates_text_pattern = re.compile('[сc]\s?\d{1,2}\.\d{1,2}\.?\s?(по|-)\s?\d{1,2}\.\d{1,2}')

    def _extract_dates(self) -> tuple:
        """Extract dates from either a filename or from pdf text string"""
        try:
            text = self._extract_pdf_text()
            dates = re.findall(self._dates_filename_pattern, self.filename)
            dates = [date.replace('_', '.') for date in dates]
            if len(dates) != 2:
                search_res = re.search(self._dates_text_pattern, text).group(0)
                search_res = search_res.split()[1:]
                dates = [s for s in search_res if 'по' not in s and '-' not in s]
            return tuple(dates)
        except:
            return None

    def _extract_pdf_text(self) -> str:
        """Extract text from pdf document"""
        with pdfplumber.open(self.filename) as f:
            text = f.pages[0].extract_text(
                keep_blank_chars=True,
                y_tolerance=0.5,
                x_tolerance=0.5
            )
        return text

    def _extract_table(self) -> None:
        """Extract a pandas DataFrame from pdf document"""
        with pdfplumber.open(self.filename) as f:
            table = f.pages[0].extract_table(
                table_settings={
                    "text_y_tolerance": 0.1,
                    "intersection_y_tolerance": 1,
                    "intersection_x_tolerance": 3,
                    "snap_y_tolerance": 0.5
                }
            )
        self.df = pd.DataFrame(table[1:], columns=table[0])

    def _get_monday(self) -> dt.datetime:
        """Returns a datetime object of monday from current week"""
        if self.dates:
            return dt.datetime(
                dt.datetime.now().year,
                int(self.dates[0].split('.')[1]),
                int(self.dates[0].split('.')[0])
            )
        else:
            return None

    def _process_empty_cols(self):
        """In case if first two columns have empty headers"""
        if not self.df.columns[0]:
            self.df.columns[0] = 'day'
        if not self.df.columns[1]:
            self.df.columns[1] = 'hours'

    def _process_columns(self) -> None:
        """Process columns names"""
        self.df = self.df.rename({
            'ДНИ': 'day',
            'ЧАСЫ': 'hours',
            'ГРУППА': 'lesson_num',
        }, axis=1)
        self._process_empty_cols()
        for i, col in enumerate(self.df.columns):
            if not col:
                self.df.columns[i] = f'empty_{i}'
            elif 'ауд' in col:
                group = self.df.columns[i - 1]
                if 'empty' in group:
                    group = self.df.columns[i - 2]
                self.df.columns[i] = group + '_loc'
        empty_columns = [col for col in self.df.columns if 'empty' in col]
        self.df.drop(empty_columns, axis=1, inplace=True)

    def _lget_list_of_dates(self, days: list) -> list:
        """Create a list of dates according to the table rows"""
        curr_day, curr_date = days[0], self._get_monday()
        dates_list = []
        for day in days:
            if day != curr_day:
                curr_date += dt.timedelta(days=1)
                curr_day = day
            dates_list.append(curr_date)
        return dates_list

    @staticmethod
    def _days_of_week(
            text: str
    ) -> str:
        """Transform initial days of week into a normal readable strings format"""
        if not text:
            return text
        text = text.replace('\n', '')
        text = text[::-1]
        return text.capitalize()

    @staticmethod
    def _merge_dt(
            date: dt.datetime,
            time: str,
            mode: str
    ) -> dt.datetime:
        """Combine a date and a time into a py datetime object"""
        time_items = time.split('-')
        time = time_items[1]
        if mode == 'start':
            time = time_items[0]
        return dt.datetime.combine(
            date.date(),
            dt.datetime.strptime(time.strip(), '%H.%M').time()
        )

    def _process_df(self):
        """Process dataframe: erase extra empty lines,
        prep days names, dates, time for start and end of lesson
        """
        while (
                self.df.iloc[0, 0] == 'НЕДЕЛИ' or
                not self.df.iloc[0, 0]
        ):
            self.df.drop(0, inplace=True)
            self.df.reset_index(inplace=True, drop=True)
        self._process_columns()
        self.df['day'] = self.df.day.map(self._days_of_week).ffill()
        self.df['date'] = self._lget_list_of_dates(list(self.df.day))
        for col in ['start', 'end']:
            self.df[col] = self.df[['date', 'hours']] \
                .apply(
                lambda x: self._merge_dt(
                    x.date,
                    x.hours,
                    mode=col
                ),
                axis=1
            )
        return self.df

    def get_schedule(self):
        """Process pdf table into a schedule format and return it"""
        try:
            self._extract_table()
            self._process_df()
            logging.info('Schedule parsing succeed!')
            return self.df
        except:
            return None


class ScheduleFilter:
    """Get the entire week schedule dataframe and prepare groups schedules"""
    df: pd.DataFrame
    schedules: dict
    _code_pattern: re.Pattern
    _teacher_pattern: re.Pattern

    def __init__(self, df: pd.DataFrame, groups: list[Group]):
        self.df = df
        self._code_pattern = re.compile(r'^[А-Я]{1,5}\s?\d{0,2}\.?\d{1,3}\.?\d{0,2}')
        self._teacher_pattern = re.compile(r'([А-Я]{1}[а-я]*)?(\-[А-Я]{1}[а-я]*)? [А-Я]\.[А-Я]\.')
        self.schedules = {group.name: None for group in groups}

    def _get_teacher(
            self,
            text: str
    ) -> str:
        """Extract teacher name from description cell"""
        text = text.replace('\n', ' ')
        try:
            return re.search(self._teacher_pattern, text).group(0)
        except:
            return ''

    def _get_subj_code(
            self,
            text: str
    ) -> str:
        """Extract subject code from description cell"""
        try:
            return re.search(self._code_pattern, text).group(0)
        except AttributeError:
            return ''

    def _get_subj(
            self,
            text: str
    ) -> str:
        """Get rid of teacher and subject code in order to get full subject name"""
        text = re.sub(self._teacher_pattern, '', text)
        text = re.sub(self._code_pattern, '', text)
        return text.strip()

    @staticmethod
    def clean_text(text: str, loc=False) -> str:
        """Clean description cell. If loc=True get rid of spaces aslo."""
        separators = ['\n', '(', ')']
        if loc:
            separators.append(' ')
        for sep in separators:
            text = text.replace(sep, '')
        return text

    def extract_groups_schedules(self):
        """Filter initial dataframe for each group and store in schedules dict"""
        common_columns = [
            'day',
            'lesson_num',
            'start',
            'end'
        ]
        for group in self.schedules.keys():
            try:
                group_columns = [col for col in self.df.columns if group in col]
                df_gr = self.df[common_columns + group_columns].copy()
                df_gr.columns = common_columns + ['subj', 'loc']
                df_gr.fillna('', inplace=True)
                df_gr['subj'] = self.df.subj.map(self.clean_text)
                df_gr['loc'] = df_gr['loc'].map(lambda x: self.clean_text(x, loc=True))
                df_gr['teacher'] = df_gr.subj.map(self._get_teacher)
                df_gr['subj_code'] = df_gr.subj.map(self._get_subj_code)
                df_gr['subj'] = df_gr.subj.map(self._get_subj)
                self.schedules[group] = df_gr
            except:
                logging.warning(f'error!!! while filtering group {group}')

    def get_group_schedule(
            self,
            group_name: str
    ) -> pd.DataFrame:
        """Return a schedule dataframe for the group"""
        return self.schedules.get(group_name)
