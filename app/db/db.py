import psycopg2
import datetime as dt
from lib.models import Group, Week, Lesson


class DB:

    def __init__(
            self,
            host: str,
            db_name: str,
            user: str,
            pg_pass: str,
            port: str
    ):
        self.conn = psycopg2.connect(
            host=host,
            database=db_name,
            user=user,
            password=pg_pass,
            port=port
        )
        self.cur = self.conn.cursor()

    def _execute_query(self, query: str, values: tuple = None):
        self.cur.execute(query, values)
        self.conn.commit()

    def get_groups(self, test=False):
        query = """select * from groups"""
        if not test:
            query = """select * from groups where name != 'test'"""
        self.cur.execute(query)
        rows = self.cur.fetchall()
        groups = []
        for row in rows:
            groups.append(Group(*row))
        return groups

    def update_group_chat(self, group_id: int, chat_id: int):
        query = """
        update users set user_type = 'regular' where group_id = %s;
        update groups set chat_id = %s where id = %s
        returning name 
        """
        self._execute_query(query, (group_id, chat_id, group_id))
        group_name = self.cur.fetchone()[0]
        return group_name

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
        return self.get_subjects()

    def get_teachers(self):
        query = """select name, id from teachers"""
        self.cur.execute(query)
        return dict(self.cur.fetchall())

    def add_teacher(self, name):
        query = f"""insert into teachers (name) values(%s)"""
        self._execute_query(query, (name,))
        return self.get_teachers()

    def add_user(self, user_id: int, group_id: int, name: str, tg_login: str, type: str = None):
        if type:
            query = f"""insert into users (user_id, group_id, name, tg_login, user_type) values(%s, %s, %s, %s, %s)"""
            self._execute_query(query, (user_id, group_id, name, tg_login, type))
        else:
            query = f"""insert into users (user_id, group_id, name, tg_login) values(%s, %s, %s, %s)"""
            self._execute_query(query, (user_id, group_id, name, tg_login))
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
                   loc: str,
                   link: str = None):
        query = f"""
        insert into lessons (week_num, day, date, start, end_t, group_id, subj_id, teacher_id, loc, link)
        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self._execute_query(query, (week_num, day, date, start, end, group_id, subj_id, teacher_id, loc, link))

    def erase_existing_schedule(self, week_num):
        query = f"""
        delete from lessons
        where week_num = %s
        """
        self._execute_query(query, (week_num, ))

    def add_file(self,
                 file_name: str,
                 uploaded_by: int,
                 tg_file_id: str
                 ):
        query = """
        insert into files (file_name, tg_file_id, uploaded_by)
        values (%s, %s, %s)
        returning id;
        """
        self.cur.execute(query, (file_name, tg_file_id, uploaded_by))
        file_id = self.cur.fetchone()[0]
        self.conn.commit()
        return file_id

    def update_file(self,
                    file_id: int,
                    file_type: str,
                    subj_id: int = None) -> str:
        if subj_id:
            query = """
            update files 
            set file_type = %s, 
            subj_id = %s 
            where id = %s
            returning file_name, tg_file_id
            """
            self.cur.execute(query, (file_type, subj_id, file_id))
        else:
            query = """
                    update files set file_type = %s where id = %s
                    returning file_name, tg_file_id
                    """
            self.cur.execute(query, (file_type, file_id))
        file_name, tg_file_id = self.cur.fetchone()
        self.conn.commit()
        return file_name, tg_file_id

    def get_schedule(self,
                     user_id: int,
                     week_num: int):
        query = """
        select 
            l.day as day,
            l.date as date,
            s.name as subject,
            l.start as start,
            l.end_t as end,
            t.name as teacher_name,
            l.loc as loc,
            l.link
        from lessons l
            left join users u
                on u.group_id = l.group_id
            left join groups g
                on g.id = l.group_id
            left join teachers t
                on t.id = l.teacher_id
            left join subjects s
                on s.id = l.subj_id
        where u.user_id = %s
        and week_num = %s
        order by date
        """
        self.cur.execute(query, (user_id, week_num))
        rows = self.cur.fetchall()
        if not rows:
            return None
        week = Week(week_num)
        for day in week.days:
            for row in rows:
                if row[0] == day.id:
                    day.schedule.append(Lesson(*list(row)[2:]))
                    day.free = False
        return week

    def get_users_ids(self, user_type='unreg'):
        if isinstance(user_type, list):
            query = """select user_id from users where user_type in %s"""
            user_type = tuple(user_type)
        elif isinstance(user_type, str):
            if user_type == 'all':
                query = """select user_id from users"""
            else:
                query = """select user_id from users where user_type= %s"""
        self.cur.execute(query, (user_type,))
        ids = [id[0] for id in self.cur.fetchall()]
        return set(ids)

    def get_users_subjects(self, user_id: int, inverted=False):
        query = """
        select 
            s.name,
            s.id 
        from lessons l
            left join subjects s
                on l.subj_id = s.id
        where group_id = (select group_id from users where user_id = %s)
        """
        self.cur.execute(query, (user_id,))
        res = self.cur.fetchall()
        if inverted:
            return dict([(r[1], r[0]) for r in res])
        return dict(res)

    def get_group_subjects(self, group_chat_id: int, inverted = False):
        query = """
        select 
            distinct
            s.name,
            s.id 
        from lessons l
            left join subjects s
                on l.subj_id = s.id
        where group_id = (select id from groups where chat_id = %s)
        """
        self.cur.execute(query, (group_chat_id,))
        res = self.cur.fetchall()
        if inverted:
            return dict([(r[1], r[0]) for r in res])
        return dict(res)


    def get_future_two_days(self, user_id, date):
        query = """
        select 
            l.date,
            l.start,
            s.id,
            s.name
        from lessons l
            left join subjects s
                on l.subj_id = s.id
        where group_id = (select group_id from users where user_id = %s)
        and date >= %s
        limit 4
        """
        self.cur.execute(query, (user_id, date))
        return self.cur.fetchall()

    def update_link(self, date, time, subj_id, link):
        query = """
        update lessons
        set link = %s
        where date = %s and
        start = %s and
        subj_id = %s;
        """
        self._execute_query(query, (link, date, time, subj_id))

    def get_users_lessons_notif(self, date: str, time: str, advance: int):
        query = """
        select 
            u.user_id,
            s.name as subject,
            l.start as start,
            l.end_t as end,
            t.name as teacher_name,
            l.loc as loc,
            l.link
        from lessons l
            left join users u
                on u.group_id = l.group_id
            left join subjects s
                on l.subj_id = s.id
            left join teachers t
                on t.id = l.teacher_id
        where 
            date = %s
            and start = %s
            and u.notifications = %s
        """
        self.cur.execute(query, (date, time, advance))
        res = self.cur.fetchall()
        users_to_notify = {}
        for row in res:
            users_to_notify[row[0]] = Lesson(*row[1:])
        return users_to_notify

    def check_notification_flag(self, user_id: int):
        query = """select notifications from users where user_id = %s"""
        self.cur.execute(query, (user_id, ))
        return self.cur.fetchone()

    def set_notifications_flag(self, user_id: int, flag: int):
        query = """
        update users set notifications = %s where user_id = %s
        """
        self._execute_query(query, (flag, user_id))


# from config import HOST_LOCAL, USER, PG_PASS, DB_NAME, PORT_LOCAL
# db = DB(host=HOST_LOCAL, user=USER, pg_pass=PG_PASS, db_name=DB_NAME, port=PORT_LOCAL)

# print(db.get_users_lessons_notif('2024-02-01', '18:40', 1))