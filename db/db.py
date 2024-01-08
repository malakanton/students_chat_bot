import psycopg2
import datetime as dt
from lib.models import Group, Week, Lesson


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
        rows = self.cur.fetchall()
        groups = []
        for row in rows:
            groups.append(Group(*row))
        return groups

    def update_group_chat(self, group_id: int, chat_id: int):
        query = """update groups set chat_id = %s where id = %s 
        returning name
        """
        self._execute_query(query, (chat_id, group_id))
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

    def get_teachers(self):
        query = """select name, id from teachers"""
        self.cur.execute(query)
        return dict(self.cur.fetchall())

    def add_teacher(self, name):
        query = f"""insert into teachers (name) values(%s)"""
        self._execute_query(query, (name,))

    def add_user(self, user_id: int, group_id: int, name: str, tg_login: str):
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
                   loc: str):
        query = f"""
        insert into lessons (week_num, day, date, start, end_t, group_id, subj_id, teacher_id, loc)
        values(%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self._execute_query(query, (week_num, day, date, start, end, group_id, subj_id, teacher_id, loc))

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
            update files set file_type = %s, set subj_id = %s where id = %s
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
            l.loc as loc
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





# #
# from config import HOST, USER, PG_PASS, DB_NAME
# db = DB(host=HOST, user=USER, pg_pass=PG_PASS, db_name=DB_NAME)
#
#
# print((db.get_user_group(123) == None))
# print(db.get_schedule(289484532, 23))



#
# groups = db.get_groups()
# print(groups)
# for id, name in groups.items():
#     query = """update groups set course=%s where id = %s"""
#     course = int(name.split('-')[1][0])
#     db._execute_query(query, (course, id))

# query = """insert into groups (name) values (%s);"""
# df, _ = get_schedule('../temp/Очно_заочное_отделение_с_2_10_по_07_10.pdf')
# groups = list(set([col for col in df.columns if (col.startswith('ИСП') or col.startswith('СС')) and not col.endswith('loc')]))
# print(groups)
# for group in sorted(groups):
#     print(query.format(group=group))
#     db._execute_query(query, (group,))

