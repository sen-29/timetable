create table timetable(
	user_id integer references users(id),
	course_id varchar(5) references courses(id),
	day integer,
	slot integer,
	primary key(user_id,course_id,day,slot)
);