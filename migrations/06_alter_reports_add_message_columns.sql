alter table reports
    add command_message_id integer default null;

alter table reports
    add bot_reply_message_id integer default null;
