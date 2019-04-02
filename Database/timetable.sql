create table timetable(
	user_id integer references users(id) on delete cascade,
	course_id varchar(5) references courses(id) on delete cascade,
	batch integer,
	day varchar(10),
	day_slot integer,
	slot integer,
	primary key(user_id,course_id,slot)
);