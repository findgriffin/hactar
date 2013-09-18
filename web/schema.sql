drop table if exists tasks;
create table tasks (
    id integer primary key autoincrement,
    text text not null,
    added integer not null,
    modified integer not null,
    due integer,
    time_start integer,
    time_finish integer,
    priority integer
);
drop table if exists nuggets;
create table nuggets (
    id integer primary key autoincrement,
    uri text, 
    text text not null, 
    added integer, 
    modified integer,
    keywords text
)
