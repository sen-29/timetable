create table offers(
	user_id integer references users(id),
	course_id varchar(5) references courses(id),
	batch integer(10),
	primary key(course_id)
);