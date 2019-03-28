create table offers(
	user_id integer references users(id),
	course_id varchar(5) references courses(id),
	room_id varchar(10),
	primary key(user_id,course_id)
);