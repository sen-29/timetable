create table requests(
    user_id int references users(id) on delete cascade,
    leave_type varchar(20),
    reason varchar(200),
    leave_date date 
);