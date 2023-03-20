import ipaddress
import json
import socket
import utils
import sys

def isCommand(string):
    commands = ["join", "leave", "register", "all", "msg", "afk", "clientlist", "block", "unblock", "pcreate", "pdisband", "pinvite", "paccept", "pdecline", "pchat", "pkick", "pleave", "pleader", "pinfo" , "partylist", "?"]
    if string in commands:
        return True
    else:
        return False

#assumes a list of string wherein each space from the original message is split into an array
def validParam(arr):
    match arr[0]: #checks first element // where the command is
        case "join": #checks if join command only contains an ip address and port
            return len(arr) == 3
        case "leave": #checks if command only contains leave
            return len(arr) == 1
        case "register": #checks if handle has a name with no space
            return len(arr) == 2
        case "all": #checks if all command has a message 
            return len(arr) >= 2
        case "msg": #checks if msg command has a handle and message
            return len(arr) >= 3
        case "afk": #checks if command only contains afk
            return len(arr) == 1
        case "clientlist": #checks if command only contains clientlist
            return len(arr) == 1
        case "block": #checks if command contains block and handle target
            return len(arr) == 2
        case "unblock": #checks if command contains unblock and handle target
            return len(arr) == 2
        case "pcreate": #checks if command contains pcreate and party name
            return len(arr) == 2
        case "pdisband": # checks if command only contains pdisband
            return len(arr) == 1
        case "pinvite": # checks if command contains pinvite and handle target
            return len(arr) == 2
        case "paccept": # checks if command contains paccept and target party
            return len(arr) == 2
        case "pdecline": # checks if command contains pdecline and target party
            return len(arr) == 2
        case "pchat": # checks if command contains pchat and the message
            return len(arr) >= 2
        case "pkick": # checks if command contains pkick and target user
            return len(arr) == 2
        case "pleave": # checks if command only contains pleave 
            return len(arr) == 1
        case "pleader": # checks if command contains pleader and target user
            return len(arr) == 2
        case "pinfo": # checks if command only contains pinfo
            return len(arr) == 1
        case "partylist": # checks if command only contains partylist
            return len(arr) == 1
        case "?": #checks if command only contains "?"
            return len(arr) == 1
        case _:
            return 0

def convertToJSON(command="", handle="", message=""):
    string = "{"
    if(command!=""):
        string+="\"command\":\""+command+"\""
        if(handle!="" or message!=""):
            string+=", "

    if(handle!=""):
        string+="\"handle\":\""+handle+"\""
        if(message!=""):
            string+=", "

    if(message!=""):
        string+="\"message\":\""+message+"\""

    return string+"}"