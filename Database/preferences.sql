create table preferences(
	user_id integer references users(id) on delete cascade,
	slot integer,
	primary key(user_id,slot)
);
