from lib.calendar_parser import get_schedule
import psycopg2
import datetime as dt


class DB:

    def __init__(
            self,
            host: str,
            db_name: str,
            user: str,
            pg_pass: str
    ):
        self.conn = psycopg2.connect(
            host=host,
            database=db_name,
            user=user,
            password=pg_pass
        )
        self.cur = self.conn.cursor()

    def _execute_query(self, query: str, values: tuple = None):
        self.cur.execute(query, values)
        self.conn.commit()

    def get_groups(self):
        query = """select * from groups"""
        self.cur.execute(query)
        groups = dict(self.cur.fetchall())
        return groups

    def get_user_group(self, user_id):
        query = f"""
        select 
            u.user_id,
            g.name
        from users u
            join groups g 
                on u.group_id=g.id
        where u.user_id = %s
        """
        self.cur.execute(query, (user_id,))
        user = self.cur.fetchone()
        return user

    def get_subjects(self):
        query = """select code, id from subjects"""
        self.cur.execute(query)
        return dict(self.cur.fetchall())

    def add_subject(self, code, name):
        query = f"""insert into subjects (code, name) values(%s, %s)"""
        self._execute_query(query, (code, name))

    def get_teachers(self):
        query = """select name, id from teachers"""
        self.cur.execute(query)
        return dict(self.cur.fetchall())

    def add_teacher(self, name):
        query = f"""insert into teachers (name) values(%s)"""
        self._execute_query(query, (name,))

    def add_user(self, user_id: int, group_id: int, name: str, tg_login: str,  date: dt.datetime):
        query = f"""insert into users (user_id, group_id, name, tg_login, added_at) values(%s, %s, %s, %s, %s)"""
        self._execute_query(query, (user_id, group_id, name, tg_login, date))
        return self.get_user_group(user_id)

    def get_weeks(self):
        query = """select week_num, min(date), max(date) 
        from lessons
        group by week_num
        """
        self.cur.execute(query)
        weeks = self.cur.fetchall()
        weeks = {week[0]: {'start': week[1], 'end': week[2]} for week in weeks}
        return weeks

    def add_lesson(self,
                   week_num: int,
                   day: int,
                   date: dt.datetime,
                   start: dt.datetime,
                   end: dt.datetime,
                   group_id: int,
                   subj_id: int,
                   teacher_id: int,
                   loc: str):
        query = f"""
        insert into lessons (week_num, day, date, start, end, group_id, subj_id, teacher_id, loc)
        values(%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self._execute_query(query, (week_num, day, date, start, end, group_id, subj_id, teacher_id, loc))

    def erase_existing_schedule(self, week_num):
        query = f"""
        delete from lessons
        where week_num = %s
        """
        self._execute_query(query, (week_num, ))


# from config import HOST, USER, PG_PASS, DB_NAME
# db = DB(host=HOST, user=USER, pg_pass=PG_PASS, db_name=DB_NAME)
# query = """insert into groups (name) values (%s);"""
# df, _ = get_schedule('../temp/Очно_заочное_отделение_с_2_10_по_07_10.pdf')
# groups = list(set([col for col in df.columns if (col.startswith('ИСП') or col.startswith('СС')) and not col.endswith('loc')]))
# print(groups)
# for group in sorted(groups):
#     print(query.format(group=group))
#     db._execute_query(query, (group,))

