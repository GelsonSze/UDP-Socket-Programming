# UDP-Socket-Programming
```
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| Command    | Parameters              | Descriptions                                                  |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /join      | <server_ip_add> <port>  | Connect to the server application.                            |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /leave     |                         | Disconnect from the server application.                       |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /register  | <handle>                | Register a unique handle or alias.                            |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /all       | <message>               | Send message to all.                                          |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /msg       | <handle> <message>      | Send direct message to a single handle.                       |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /afk       |                         | Set yourself to afk, no one can message you but you           |
|            |                         | can still see global messages. Performing any action          |
|            |                         | will unset your afk status if you were afk.                   |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /clientlist|                         | Checks all the active and afk (if enabled) users in the server|
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /block     | <handle>                | Block the selected user, neither the blocked user or          |
|            |                         | you can message each other but the blocked user can           |
|            |                         | still see your global messages.                               |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /unblock   | <handle>                | Unblock the selected user.                                    |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /pcreate   | <message>               | Create a party with the message being the party name.         |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /pdisband  |                         | Disband the party you are in.                                 |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /pinvite   | <handle>                | Invite a user into your current party.                        |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /paccept   | <message>               | Accept the party invite.                                      |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /pdecline  | <message>               | Decline the party invite.                                     |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /pchat     | <message>               | Send a message to all the users in the party.                 |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /pkick     | <handle>                | Kick the selected user out of the current party.              |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /pleave    |                         | Leave the current party you are in.                           |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /pleader   | <handle>                | Transfer party leadership to the selected user                |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /pinfo     |                         | Prints out the information of the party.                      |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /partylist |                         | Checks all the current parties of the server.                 |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
| /?         |                         | Request command help to output all Input Syntax commands for  |
|            |                         | references                                                    |
+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+
```
