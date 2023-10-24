CREATE TABLE reports (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    reporter_id INT NOT NULL,
    reported_user_id INT NOT NULL,
    chat_id BIGINT NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolution_time TIMESTAMP,
    reported_message_id BIGINT NOT NULL,
    reported_message_content VARCHAR(4096) NOT NULL,
    resolved_by_id INT,
    status varchar(32) NOT NULL,


    CONSTRAINT reports_reporter_FK FOREIGN KEY (reporter_id) REFERENCES users(id),
    CONSTRAINT reports_reported_user_FK FOREIGN KEY (reported_user_id) REFERENCES users(id),
    CONSTRAINT reports_chat_FK FOREIGN KEY (chat_id) REFERENCES chats(chat_id),
    CONSTRAINT reports_resolved_by_FK FOREIGN KEY (resolved_by_id) REFERENCES users(id)
);
