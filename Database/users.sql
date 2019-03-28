create table users(
	id integer primary key auto_increment,
	name varchar(50) not null,
	email varchar(100) not null,
	mobile varchar(10) not null unique,
	password varchar(20),
	isadmin boolean not null default false,
	birthdate date
);
