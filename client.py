import sys
import socket
import json
import utils
import threading

address             = None
port                = None
connected           = False
bufferSize          = 1024
receiveThread       = None
stopThread          = False

def receiveDatagram():
    while not address is None and not port is None:
        global stopThread
        global receiveThread
        if stopThread:
            receiveThread = None
            return
        try:
            UDPClientSocket.settimeout(1)
            msgFromServer = UDPClientSocket.recvfrom(bufferSize)
            if(msgFromServer != None and msgFromServer[0]):
                msg = json.loads(msgFromServer[0], strict=False)
                if "message" in msg:
                    print(msg["message"])
        except socket.timeout:
            continue
        except Exception as e:
            disconnect()
            print("Error has occurred trying to reach the server.")
            print("Disconnecting......")


def disconnect():
    global connected
    global address
    global port
    global stopThread
    connected = False
    address = None
    port = None
    stopThread = True

# Create a UDP socket at client side

try:
    UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as e:
    sys.exit(f'Failed to create socket - {e}')
    
try:
    while (True):
        msgFromClient = input()
        msgArr = msgFromClient.strip()

        if len(msgArr)<=1 or msgArr[0] != "/":
            print("Error: Command not found.")
        else:
            msgArr = msgArr[1:].split()
            if len(msgArr) > 0 and utils.isCommand(msgArr[0]):
                if (utils.validParam(msgArr)):
                    match msgArr[0]:
                        #/join command
                        case "join":
                            try:
                                if(not connected):
                                    UDPClientSocket.settimeout(1)
                                    bytesToSend = str.encode(utils.convertToJSON(command="join"))
                                    UDPClientSocket.sendto(bytesToSend, (msgArr[1], int(msgArr[2])))
                                    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
                                    if(msgFromServer[0]):
                                        msg = json.loads(msgFromServer[0])
                                        if "message" in msg:
                                            connected = True
                                            address = msgArr[1]
                                            port = int(msgArr[2])
                                            print(msg["message"])
                                            stopThread = False
                                            receiveThread = threading.Thread(target=receiveDatagram)
                                            receiveThread.start()
                                    else:
                                        raise socket.timeout
                                else:
                                    print("Error: Already connected to a server")
                            except ValueError:
                                print("Error: Invalid port number")
                            except (socket.timeout, socket.error):
                                if(connected):
                                    print("Request timed out.")
                                    print("Disconnecting......")
                                else:
                                    print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")

                                disconnect()
                                continue

                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #/leave command
                        case "leave":
                            try:
                                if(connected):
                                    stopThread = True #stop the receving thread

                                    #waiting for thread to end
                                    while receiveThread != None:
                                        continue

                                    bytesToSend = str.encode(utils.convertToJSON(command="leave"))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
                                    if(msgFromServer[0]):
                                        msg = json.loads(msgFromServer[0])
                                        if "message" in msg:
                                            disconnect()
                                            print(msg["message"])
                                    else:
                                        raise socket.error
                                else:
                                    print("Error: Disconnection failed. Please connect to the server first.")
                            except (socket.timeout, socket.error) as e:
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #/register command
                        case "register":
                            try:
                                if(connected):
                                    handle = msgArr[1].replace('\"', '\'')
                                    bytesToSend = str.encode(utils.convertToJSON(command="register", handle=handle))
                                    msg = bytesToSend
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Registration failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #/all command
                        case "all":
                            try:
                                if(connected):
                                    message = ' '.join(msgArr[1:])
                                    message = message.replace('\"', '\'')
                                    bytesToSend = str.encode(utils.convertToJSON(command="all", message=message))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #/msg command
                        case "msg":
                            try:
                                if(connected):
                                    message = ' '.join(msgArr[2:])
                                    message = message.replace('\"', '\'')
                                    bytesToSend = str.encode(utils.convertToJSON(command="msg", handle=msgArr[1], message=message))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #afk user
                        case "afk":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="afk"))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #get current server client list
                        case "clientlist":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="clientlist"))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #block a user
                        case "block":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="block", handle=msgArr[1]))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #block a user
                        case "unblock":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="unblock", handle=msgArr[1]))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #create party
                        case "pcreate":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="pcreate", message=msgArr[1]))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #disband party
                        case "pdisband":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="pdisband"))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #sending party invite
                        case "pinvite":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="pinvite", handle=msgArr[1]))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #accepting party invite
                        case "paccept":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="paccept", message=msgArr[1]))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #decline party invite
                        case "pdecline":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="pdecline", message=msgArr[1]))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #send message to party chat
                        case "pchat":
                            try:
                                if(connected):
                                    message = ' '.join(msgArr[1:])
                                    message = message.replace('\"', '\'')
                                    bytesToSend = str.encode(utils.convertToJSON(command="pchat", message=message))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #send message to party chat
                        case "pkick":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="pkick", handle=msgArr[1]))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #send message to party chat
                        case "pleave":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="pleave"))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #send message to party chat
                        case "pleader":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="pleader", handle=msgArr[1]))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue
                        
                        #send message to party chat
                        case "pinfo":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="pinfo"))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #send message to party chat
                        case "partylist":
                            try:
                                if(connected):
                                    bytesToSend = str.encode(utils.convertToJSON(command="partylist"))
                                    UDPClientSocket.sendto(bytesToSend, (address , port))
                                else:
                                    print("Error: Message failed. Please connect to the server first.")
                            except (socket.timeout, socket.error):
                                disconnect()
                                print("Request timed out.")
                                print("Disconnecting......")
                                continue
                            except Exception as e:
                                disconnect()
                                print(f'Error Occured - {e}')
                                continue

                        #/? command
                        case "?":
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| Command    | Parameters              | Descriptions                                                  |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /join      | <server_ip_add> <port>  | Connect to the server application.                            |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /leave     |                         | Disconnect from the server application.                       |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /register  | <handle>                | Register a unique handle or alias.                            |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /all       | <message>               | Send message to all.                                          |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /msg       | <handle> <message>      | Send direct message to a single handle.                       |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /afk       |                         | Set yourself to afk, no one can message you but you           |")
                            print("|            |                         | can still see global messages. Performing any action          |")
                            print("|            |                         | will unset your afk status if you were afk.                   |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /clientlist|                         | Checks all the active and afk (if enabled) users in the server|")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /block     | <handle>                | Block the selected user, neither the blocked user or          |")
                            print("|            |                         | you can message each other but the blocked user can           |")
                            print("|            |                         | still see your global messages.                               |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /unblock   | <handle>                | Unblock the selected user.                                    |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /pcreate   | <message>               | Create a party with the message being the party name.         |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /pdisband  |                         | Disband the party you are in.                                 |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /pinvite   | <handle>                | Invite a user into your current party.                        |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /paccept   | <message>               | Accept the party invite.                                      |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /pdecline  | <message>               | Decline the party invite.                                     |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /pchat     | <message>               | Send a message to all the users in the party.                 |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /pkick     | <handle>                | Kick the selected user out of the current party.              |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /pleave    |                         | Leave the current party you are in.                           |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /pleader   | <handle>                | Transfer party leadership to the selected user                |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /pinfo     |                         | Prints out the information of the party.                      |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /partylist |                         | Checks all the current parties of the server.                 |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                            print("| /?         |                         | Request command help to output all Input Syntax commands for  |")
                            print("|            |                         | references                                                    |")
                            print("+────────────+─────────────────────────+───────────────────────────────────────────────────────────────+")
                else:
                    print("Error: Command parameters do not match or is not allowed.")
            else:
                print("Error: Command not found.")
except Exception as e:
    stopThread = True
    print(f'Error Exception in While loop - {e}')
