create table preferences(
	user_id integer references users(id),
	slot integer,
	primary key(user_id,slot)
);
