CREATE TABLE chat_settings (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    chat_id BIGINT,
    karmic_restrictions BOOLEAN DEFAULT false,
    CONSTRAINT chat_settings_FK FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
);