# KarmaBot

![Лого проекта](./docs/pictures/gitgub_titlepic.png)

This telegram bot is designed to track karma in chats.
Just add him to the chat and thank each other for helpful answers.

For deploy info look at [docs/deploy_manual.md](./docs/deploy_manual.md)

most bot command used throttle mechanism, it mean bot don't answer if you send many identical requests in a row

commands list:
* /start, !start - simple info about bot
* !help - info about karmas triggers
* !about - info about bot author and link to source code
* !top - view top of karma for users of that chat (works only for group and supergroups)
* !me - view yours karma for that chat (in group or supergroup) or your karmas in all yours chat (in private)
* !report, /report, !admin, /admin, @admin - reporting to group administrators for message with spam, insult 
or another inappropriate content

superuser commands list:
* /generate_invite_logchat - if bot is admin in chat of LOG_CHAT_ID from config.py bot generate invite link to that
* /logchat - get logchat invite link if it's generated earlier
* /update_log - send logs from /logs path to LOG_CHAT_ID and remove logs from files
* /idchat - get id of chat   
* /dump - bot send to DUMP_CHAT_ID sqlite file
* /json - bot export db with karma to json and send to DUMP_CHAT_ID
* !add_manual - send it with format  "!add_manual USER_ID NEW_KARMA" for replace karma in that chat of that user.
**use this command CAREFULLY**
