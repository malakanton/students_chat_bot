from loader import db

create_teachers_query = """
create table if not exists teachers (
    id serial primary key,
    name varchar(50) unique not null,
    phone_number varchar(20),
    email varchar(50),
    comment varchar(255)
)
"""
create_users_query = """
create table if not exists users (
    user_id smallint primary key not null,
    group_id integer not null,
    name varchar(30),
    
    foreign key (group_id)
        references groups (id)
)
"""
create_files_query = """
create table if not exists files (
	id serial primary key,
	file_type varchar(10) not null,
	file_name varchar(255) not null,
	file_path varchar(255) not null,
	subj_id smallint,
	uploaded_at date not null,
	uploaded_by bigint not null,
	
	foreign key (uploaded_by)
		references users (user_id),
	foreign key (subj_id)
		references subjects (id)
)
"""
create_subjects_query = """
create table if not exists subjects (
    id serial primary key not null,
    code varchar(10) unique not null,
    name varchar(50) not null,
    comment varchar(20)
)
"""
create_groups_query = """
create table if not exists groups (
    id serial primary key not null,
    name varchar(10) not null
)
"""
create_lessons_query = """
create table if not exists lessons (
    id serial primary key not null,
    week_num smallint not null,
    date date not null,
    start time not null,
    end_t time not null,
    group_id smallint not null,
    subj_id smallint not null,
    teacher_id smallint,
    loc varchar(10),
    
    foreign key (group_id)
        references groups (id),
    foreign key (subj_id)
        references subjects (id),
    foreign key (teacher_id)
        references teachers (id)
)
"""

tables = [
    create_teachers_query,
    create_groups_query,
    create_subjects_query,
    create_users_query,
    create_files_query,
    create_lessons_query
]


def create_tables(tables:list):
    for table_query in tables:
        db._execute_query(table_query)


create_tables(tables)
