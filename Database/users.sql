create table users(
	id serial primary key,
	name varchar(50) not null,
	email varchar(100) not null,
	mobile char(10) not null unique,
	password varchar(20) not null,
	isadmin boolean not null default false,
	birthdate date
);
