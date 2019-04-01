create table slots(
    course_id varchar(5) references courses(id),
    slot integer not null,
    primary key(course_id)
);