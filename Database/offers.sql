create table offers(
	user_id integer references users(id) on delete cascade,
	course_id varchar(5) references courses(id) on delete cascade,
	batch integer,
	primary key(course_id)
);