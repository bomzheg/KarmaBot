# KarmaBot

![Лого проекта](./docs/pictures/gitgub_titlepic.png)

This telegram bot is designed to track karma in chats.
Just add him to the chat and thank each other for helpful answers.

[![wakatime](https://wakatime.com/badge/github/bomzheg/KarmaBot.svg)](https://wakatime.com/badge/github/bomzheg/KarmaBot)

- [Deployment](./docs/deploy_manual.md)
- [Development](./docs/development.md)

Most bot commands use throttle mechanism, it means the bot wouldn't answer if you send many identical requests in a row.

Commands list:
* /start, !start - simple bot information
* !help - information about karma triggers
* !about - information about the bot author and link to the source code
* !top - show top users by karma level for this chat (only works for group and supergroups)
* !me - show your karma for this chat (in group or supergroup) or show your karma for all yours chats (in private)
* !report, /report, !admin, /admin, @admin - report spam, insult or another inappropriate content
to the group administrators
* !settings - show chat settings and commands to change them

Moderator commands list:
* !ro !mute [DURATION] [@mention] - restrict replied or mentioned user for DURATION.
* !ban [DURATION] [@mention] - kick replied user for DURATION
  * DURATION in format [AAAy][BBBw][CCCd][DDDh][EEEm][FFFs] where:
    * AAA - count of years (more than one year is permanent)
    * BBB - count of weeks
    * CCC - count of days
    * DDD - count of hours
    * EEE - count of minutes
    * FFF - count of seconds (less than 30 seconds will be mean 30 seconds)
  * you have to specify one or more duration part without spaces
* !warn, !w [@mention] - official warn user from moderator
* !info [@mention] - information about user (karma changes, restrictions, warns)


Chat settings commands list:
* !enable_karma - enable karma in chat
* !disable_karma - disable karma in chat
* !enable_karmic_ro - enable restrictions on low karma reason
  (need to have right for ban users for bot and user asked for that command)
* !disable_karmic_ro - disable restrictions on low karma reason
  (need to have right for ban users for bot and user asked for that command)
* !set_report_reward [REWARD] - set reward for report


Helper commands list:
* !idchat - get id of chat, your id, and id of replayed user (if you reply to someone)
* !go - search in Google
* !paste - services for paste code
* !nm - information about meta-questions
* !xy - information about XY problem


Superuser commands list:
* /generate_invite_logchat - if bot is admin in the chat of LOG_CHAT_ID from `config.py` bot generates invite link to that
* /logchat - get logchat invite link if it's generated earlier
* /update_log - send logs from /logs path to LOG_CHAT_ID and remove logs from files
* /dump - The bot sends a dump of the sqlite database to the chat DUMP_CHAT_ID
* /json - bot exports db with karma to json and send it to the DUMP_CHAT_ID
* !add_manual - send it with the format  "!add_manual USER_ID NEW_KARMA" to replace karma in that chat for that user.
**use this command CAREFULLY**
