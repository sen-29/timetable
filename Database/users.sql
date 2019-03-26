    create table users(
        id integer primary key,
        username varchar(20) not null unique,
        password varchar(20) not null,
        isadmin boolean not null default FALSE
    );