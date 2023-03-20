import sys
import socket
import json
import utils

ALLOW_AFK = True
ALLOW_BLOCK = True
ALLOW_PARTY = True

localIP         = "127.0.0.1"
localPort       = 12345
bufferSize      = 1024
clientHandle    = {}
afkList         = []
blockList       = {}
partyList       = {}

def setNotAFK(address):
    if address in afkList:
        handle = clientHandle[address]
        bytesToSend = str.encode(utils.convertToJSON(message=f'{handle} is no longer AFK.'))
        afkList.remove(address)
        broadcast(bytesToSend, blockmessage=True)

def multicast(bytesToSend, clients, blockmessage=False):
    if ALLOW_BLOCK and blockmessage:
        for users in clients:
            try:
                if(clientHandle.get(users) != None):
                    clientAddress = (users[0], users[1])
                    if(address in blockList[users]):
                        continue
                    else:
                        sendData(bytesToSend, clientAddress)
            except (socket.error, socket.timeout):
                clientHandle.pop(clientAddress)
                continue
    else:
        for users in clients:
            try:
                if(clientHandle.get(users) != None):
                    clientAddress = (users[0], users[1])
                    sendData(bytesToSend, clientAddress)
            except (socket.error, socket.timeout):
                clientHandle.pop(clientAddress)
                continue

def broadcast(bytesToSend, blockmessage=False):
    if ALLOW_BLOCK and blockmessage:
        for clients in clientHandle:
            try:
                if(clientHandle.get(clients) != None):
                    clientAddress = (clients[0], clients[1])
                    if(address in blockList[clients]):
                        continue
                    else:
                        sendData(bytesToSend, clientAddress)
            except (socket.error, socket.timeout):
                clientHandle.pop(clientAddress)
                continue
    else:
        for clients in clientHandle:
            try:
                if(clientHandle.get(clients) != None):
                    clientAddress = (clients[0], clients[1])
                    sendData(bytesToSend, clientAddress)
            except (socket.error, socket.timeout):
                clientHandle.pop(clientAddress)
                continue

def sendData(bytesToSend, address):
    try:
        UDPServerSocket.sendto(bytesToSend, address)
    except (socket.error, socket.timeout):
        clientHandle.pop(address)
        return

# Create a datagram socket
try:
    UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as e:
    sys.exit(f'Failed to create socket - {e}')
    

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")
print(f'Listening from {localIP}, port: {localPort}')

# Listen for incoming datagrams
while(True):
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0] #sender message json object
        address = bytesAddressPair[1] #sender address

        print(f'Client IP Address:{address}')
        print(f'Message from Client:{message}')
        msg = json.loads(message.decode())

        if ALLOW_AFK:
            if(msg["command"] == "afk" or msg["command"] == "leave"):
                pass
            else:
                setNotAFK(address)
                
        match(msg["command"]):
            case "join":
                if(address not in clientHandle):
                    clientHandle[address] = None
                    blockList[address] = []
                    bytesToSend = str.encode(utils.convertToJSON(message="Connection to the Message Board Server is successful!"))
                    print(clientHandle)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message = "Already connected to the Message Board Server"))

                sendData(bytesToSend, address)

            case "leave":
                if address in clientHandle:
                    handle = clientHandle.get(address)
                    bytesToSendReceiver = str.encode(utils.convertToJSON(message=f'{handle} has left the server.'))
                    clientHandle.pop(address)
                    blockList.pop(address)
                    print(clientHandle)
                    bytesToSend = str.encode(utils.convertToJSON(message="Connection closed. Thank you!"))
                    sendData(bytesToSend, address)
                    broadcast(bytesToSendReceiver)
                    if ALLOW_PARTY:
                        currentParty = None
                        for party in partyList:
                            if address in partyList[party]["users"]:
                                currentParty = party #get current party of user
                                break
                        if currentParty != None:
                            partyList[currentParty]["users"].remove(address)
                            receiverList = partyList[currentParty]["users"]
                            bytesToSend = str.encode(utils.convertToJSON(message=f'{handle} left the party.'))
                            multicast(bytesToSend, receiverList)

                            if partyList[currentParty]["users"] == [] or partyList[currentParty]["leader"] == address:
                                partyList.pop(currentParty)
                                bytesToSend = str.encode(utils.convertToJSON(message=f'Party {currentParty} has been disbanded.'))
                                print(partyList)
                                broadcast(bytesToSend)
                    
            case "register":
                if( address in clientHandle.keys() #client is in the client-username dictionary
                    and clientHandle.get(address) == None #client doesnt have a username yet
                    and msg["handle"] not in clientHandle.values()): #handle given is not existing yet

                    clientHandle[address] = msg["handle"]
                    print(clientHandle)
                    bytesToSend = str.encode(utils.convertToJSON(message=f'Welcome {msg["handle"]}!'))
                    broadcast(bytesToSend)

                elif clientHandle.get(address) != None:
                    bytesToSend = str.encode(utils.convertToJSON(command="error", message="Error: Already registered."))
                    sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(command="error", message="Error: Registration failed. Handle or alias already exists."))
                    sendData(bytesToSend, address)

            case "all":
                if( clientHandle[address] != None  #client username exists
                    and msg["message"] != ""): #message of client is not empty
                    senderHandle = clientHandle.get(address)
                    bytesToSend = str.encode(utils.convertToJSON(message=f'{senderHandle}: {msg["message"]}'))
                    broadcast(bytesToSend, blockmessage=True)
                    
                elif clientHandle[address] == None:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                    sendData(bytesToSend, address)
            
            case "msg":
                if( clientHandle[address] != None  #client username exists
                    and msg["handle"] in clientHandle.values() #handle receiver exists
                    and msg["message"] != ""): #message of client is not empty

                    receiverAddress =  list(clientHandle.keys())[list(clientHandle.values()).index(msg["handle"])]
                    senderHandle = clientHandle.get(address)
                    bytesToSend = str.encode(utils.convertToJSON(message=f'[To {msg["handle"]}]: {msg["message"]}'))
                    bytesToSendReceiver = str.encode(utils.convertToJSON(message=f'[From {senderHandle}]: {msg["message"]}'))

                    if ALLOW_AFK and receiverAddress not in afkList:
                        if ALLOW_BLOCK:
                            if receiverAddress not in blockList[address] and address not in blockList[receiverAddress]:
                                sendData(bytesToSend, address)  
                                sendData(bytesToSendReceiver, receiverAddress)
                            elif receiverAddress in blockList[address]:
                                bytesToSend = str.encode(utils.convertToJSON(message=f'{msg["handle"]} is currently blocked.'))
                                sendData(bytesToSend, address)
                            elif address in blockList[receiverAddress]:
                                bytesToSend = str.encode(utils.convertToJSON(message=f'{msg["handle"]} currently has you blocked.'))
                                sendData(bytesToSend, address)
                        else:
                            sendData(bytesToSend, address)  
                            sendData(bytesToSendReceiver, receiverAddress)

                    elif ALLOW_AFK and receiverAddress in afkList:
                        bytesToSend = str.encode(utils.convertToJSON(message=f'{msg["handle"]} is currently AFK, please try again later.'))
                        sendData(bytesToSend, address)
                    else:
                        sendData(bytesToSend, address)
                        sendData(bytesToSendReceiver, receiverAddress)

                elif clientHandle[address] == None:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                    sendData(bytesToSend, address)
                elif msg["handle"] not in clientHandle.values():
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Handle or alias not found"))
                    sendData(bytesToSend, address)

            case "afk":
                if ALLOW_AFK:
                    if clientHandle[address] != None:  #client username exists
                        senderHandle = clientHandle.get(address)
                        if address not in afkList:
                            bytesToSend = str.encode(utils.convertToJSON(message=f'{senderHandle} is now AFK.'))
                            afkList.append(address)
                            broadcast(bytesToSend, blockmessage=True)
                        else:
                            setNotAFK(address)
                        
                    elif clientHandle[address] == None:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                        continue
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: AFK feature is currently disabled"))
                    sendData(bytesToSend, address)

            #client list
            case "clientlist":
                if ALLOW_AFK:
                    if(clientHandle[address] != None): #client username exists
                        onlineClients = []
                        afkClients = []
                        for client in clientHandle:
                            clientUsername = clientHandle.get(client)
                            if(client in afkList):
                                afkClients.append(clientUsername)
                            else:
                                onlineClients.append(clientUsername)

                        onlineClients = ", ".join(onlineClients)
                        afkClients = ", ".join(afkClients)

                        bytesToSend = str.encode(utils.convertToJSON(message=f'Online Clients: {onlineClients}\nAFK Clients: {afkClients}'))
                        sendData(bytesToSend, address)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    if(clientHandle[address] != None): #client username exists
                        onlineClients = []
                        for client in clientHandle:
                            clientUsername = clientHandle.get(client)
                            onlineClients.append(clientUsername)

                        onlineClients = ", ".join(onlineClients)

                        bytesToSend = str.encode(utils.convertToJSON(message=f'Online Clients: {onlineClients}'))
                        sendData(bytesToSend, address)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)

            case "block":
                if ALLOW_BLOCK:
                    if( clientHandle[address] != None #client username exists
                        and msg["handle"] in clientHandle.values()):  #blocked client username exists

                        blockTarget = msg["handle"]
                        blockTargetAddress =  list(clientHandle.keys())[list(clientHandle.values()).index(msg["handle"])]
                        if blockTarget == clientHandle[address]:
                            bytesToSend = str.encode(utils.convertToJSON(message=f'Error: You cannot block yourself.'))
                        elif blockTargetAddress not in blockList[address]:
                            blockList[address].append(blockTargetAddress)
                            print(blockList[address])
                            bytesToSend = str.encode(utils.convertToJSON(message=f'{blockTarget} is now blocked.'))
                        elif blockTargetAddress in blockList[address]:
                            bytesToSend = str.encode(utils.convertToJSON(message=f'{blockTarget} is already blocked.'))
                            
                        sendData(bytesToSend, address)
                            
                    elif clientHandle[address] == None:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                    elif msg["handle"] not in clientHandle.values():
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Handle or alias not found"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Block feature is currently disabled"))
                    sendData(bytesToSend, address)

            case "unblock":
                if ALLOW_BLOCK:
                    if( clientHandle[address] != None #client username exists
                        and msg["handle"] in clientHandle.values()):  #blocked client username exists

                        blockTarget = msg["handle"]
                        blockTargetAddress =  list(clientHandle.keys())[list(clientHandle.values()).index(msg["handle"])]
                        if blockTargetAddress in blockList[address]:
                            blockList[address].remove(blockTargetAddress)
                            bytesToSend = str.encode(utils.convertToJSON(message=f'{blockTarget} is now unblocked.'))
                            sendData(bytesToSend, address)
                        elif blockTargetAddress not in blockList[address]:
                            bytesToSend = str.encode(utils.convertToJSON(message=f'{blockTarget} is not blocked.'))
                            sendData(bytesToSend, address)
                            
                    elif clientHandle[address] == None:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                    elif msg["handle"] not in clientHandle.values():
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Handle or alias not found"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Unblock feature is currently disabled"))
                    sendData(bytesToSend, address)

            #create party
            case "pcreate":
                if ALLOW_PARTY:
                    if(clientHandle[address] != None): #client username exists
                        inParty = False
                        for party in partyList:
                            if address in partyList[party]["users"]:
                                inParty = True #check if user is in a party
                                break

                        if msg["message"] not in partyList and not inParty:
                            partyList[msg["message"]] = {"users": [address], "invited": [], "leader": address}
                            bytesToSend = str.encode(utils.convertToJSON(message=f'Party {msg["message"]} has been created.'))
                            print(partyList)
                        elif inParty:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: Cannot create party while in a party."))
                        elif msg["message"] in partyList:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: Party name already taken."))
                        
                        sendData(bytesToSend, address)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)

            #disband current party
            case "pdisband":
                if ALLOW_PARTY:
                    if(clientHandle[address] != None): #client username exists
                        currentParty = None
                        for party in partyList:
                            if address in partyList[party]["users"]:
                                currentParty = party #get current party of user
                                break
                        if currentParty == None:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: You are currently not in a party."))
                            sendData(bytesToSend, address)
                        elif address == partyList[currentParty]["leader"]:
                            partyList.pop(currentParty)
                            bytesToSend = str.encode(utils.convertToJSON(message=f'Party {currentParty} has been disbanded.'))
                            print(partyList)
                            broadcast(bytesToSend)
                        else:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: Only party leaders can disband parties."))
                            sendData(bytesToSend, address)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)

            #invite to party
            case "pinvite":
                if ALLOW_PARTY:
                    if( clientHandle[address] != None #client username exists
                        and msg["handle"] in clientHandle.values()): #receiver username exists
                        currentParty = None
                        invitedTarget = msg["handle"]
                        invitedTargetAddress = list(clientHandle.keys())[list(clientHandle.values()).index(msg["handle"])]
                        targetInParty = False
                        for party in partyList:
                            if(address in partyList[party]["users"]):
                                currentParty = party #get current party of user
                            if(invitedTargetAddress in partyList[party]["users"]):
                                targetInParty = True

                        if currentParty == None:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: You are currently not in a party."))
                            sendData(bytesToSend, address)
                        elif ALLOW_BLOCK and address in blockList[invitedTargetAddress]:
                            bytesToSend = str.encode(utils.convertToJSON(message=f'{invitedTarget} has you blocked. Failed to send party invite.'))
                            sendData(bytesToSend, address)
                        elif ALLOW_BLOCK and invitedTargetAddress in blockList[address]:
                            bytesToSend = str.encode(utils.convertToJSON(message=f'You have {invitedTarget} blocked. Failed to send party invite.'))
                            sendData(bytesToSend, address)
                        elif targetInParty:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: Invited user is already in a party."))
                            sendData(bytesToSend, address)
                        elif invitedTargetAddress in partyList[currentParty]["invited"]:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: Already invited user in the party."))
                            sendData(bytesToSend, address)
                        else:
                            partyList[currentParty]["invited"].append(invitedTargetAddress)
                            bytesToSendTarget = str.encode(utils.convertToJSON(message=f'{clientHandle.get(address)} invited you to join party {currentParty}. Type /paccept {currentParty} to accept the invite and /pdecline {currentParty} to decline the invite.'))
                            bytesToSendSender = str.encode(utils.convertToJSON(message=f'Invited {invitedTarget} to join party {currentParty}.'))
                            sendData(bytesToSendSender,address)
                            sendData(bytesToSendTarget,invitedTargetAddress)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)

            #accept party invite
            case "paccept":
                if ALLOW_PARTY:

                    currentParty = None
                    for party in partyList:
                        if address in partyList[party]["users"]:
                            currentParty = party #get current party of user
                            break

                    if( clientHandle[address] != None #client username exists
                        and msg["message"] in partyList.keys() #party name exists
                        and address in partyList[msg["message"]]["invited"] #client is invited in the party
                        and currentParty == None): #client is not in a party
                        
                        partyList[msg["message"]]["invited"].remove(address)
                        partyList[msg["message"]]["users"].append(address)
                        bytesToSend = str.encode(utils.convertToJSON(message=f'Successfully joined party {msg["message"]}.'))
                        sendData(bytesToSend, address)

                        receiverList = partyList[msg["message"]]["users"]
                        bytesToSendParty = str.encode(utils.convertToJSON(message=f'{clientHandle[address]} has joined the party.'))
                        multicast(bytesToSendParty, receiverList)

                    elif msg["message"] not in partyList.keys():
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Party doesn't exist"))
                        sendData(bytesToSend, address)
                    elif address not in partyList[msg["message"]]["invited"]:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: You are not invited in the party."))
                        sendData(bytesToSend, address)
                    elif currentParty != None:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: You are already in a party."))
                        sendData(bytesToSend, address)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                    
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)
            
            #decline party invite
            case "pdecline":
                if ALLOW_PARTY:

                    currentParty = None
                    for party in partyList:
                        if address in partyList[party]["users"]:
                            currentParty = party #get current party of user
                            break

                    if( clientHandle[address] != None #client username exists
                        and msg["message"] in partyList.keys() #party name exists
                        and address in partyList[msg["message"]]["invited"] #client is invited in the party
                        and currentParty == None):#client is not in a party
                        
                        partyList[msg["message"]]["invited"].remove(address)
                        bytesToSend = str.encode(utils.convertToJSON(message=f'Successfully declined party {msg["message"]}\'s invite.'))
                        sendData(bytesToSend, address)

                        bytesToSendParty = str.encode(utils.convertToJSON(message=f'{clientHandle[address]} declined the party invite.'))
                        receiverList = partyList[msg["message"]]["users"]
                        multicast(bytesToSendParty, receiverList)

                    elif msg["message"] not in partyList.keys():
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Party doesn't exist"))
                        sendData(bytesToSend, address)
                    elif address not in partyList[msg["message"]]["invited"]:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: You are not invited in the party."))
                        sendData(bytesToSend, address)
                    elif currentParty != None:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: You are already in a party."))
                        sendData(bytesToSend, address)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)

            #party chat
            case "pchat":
                if ALLOW_PARTY:
                    if( clientHandle[address] != None #client username exists
                        and msg["message"] != ""): #message string is not empty
                        currentParty = None
                        for party in partyList:
                            if address in partyList[party]["users"]:
                                currentParty = party #get current party of user
                                break

                        if currentParty == None:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: You are currently not in a party."))
                            sendData(bytesToSend, address)
                        else:
                            senderHandle = clientHandle.get(address)
                            receiverList = partyList[currentParty]["users"]
                            bytesToSend = str.encode(utils.convertToJSON(message=f'[Party Chat] {senderHandle}: {msg["message"]}'))

                            multicast(bytesToSend, receiverList, blockmessage=True)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)

            #party kick
            case "pkick":
                if ALLOW_PARTY:
                    if( clientHandle[address] != None #client username exists
                        and msg["handle"] in clientHandle.values()): #receiver username exists
                        currentParty = None
                        targetHandle = msg["handle"]
                        targetAddress = list(clientHandle.keys())[list(clientHandle.values()).index(msg["handle"])]

                        for party in partyList:
                            if address in partyList[party]["users"]:
                                currentParty = party #get current party of user
                                break
                        if currentParty == None:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: You are currently not in a party."))
                            sendData(bytesToSend, address)
                        elif targetAddress not in partyList[currentParty]["users"]:
                            bytesToSend = str.encode(utils.convertToJSON(message=f'Error: {targetHandle} is not in the party'))
                            sendData(bytesToSend, address)
                        elif targetHandle == clientHandle[address]:
                            bytesToSend = str.encode(utils.convertToJSON(message=f'Error: You cannot kick yourself out of the party.'))
                            sendData(bytesToSend, address)
                        elif address == partyList[currentParty]["leader"]:
                            partyList[currentParty]["users"].remove(targetAddress)
                            bytesToSend = str.encode(utils.convertToJSON(message=f'{targetHandle} has been kicked out of the party.'))
                            receiverList = partyList[currentParty]["users"]
                            multicast(bytesToSend, receiverList)
                        else:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: Only party leaders can kick users."))
                            sendData(bytesToSend, address)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)
            
            #leave current party
            case "pleave":
                if ALLOW_PARTY:
                    if(clientHandle[address] != None): #client username exists
                        currentParty = None
                        for party in partyList:
                            if address in partyList[party]["users"]:
                                currentParty = party #get current party of user
                                break
                        if currentParty == None:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: You are currently not in a party."))
                            sendData(bytesToSend, address)
                        else:
                            partyList[currentParty]["users"].remove(address)
                            bytesToSend = str.encode(utils.convertToJSON(message=f'You have left the party.'))
                            sendData(bytesToSend, address)

                            receiverList = partyList[currentParty]["users"]
                            bytesToSend = str.encode(utils.convertToJSON(message=f'{clientHandle[address]} left the party.'))
                            multicast(bytesToSend, receiverList)

                            if partyList[currentParty]["users"] == [] or partyList[currentParty]["leader"] == address:
                                partyList.pop(currentParty)
                                bytesToSend = str.encode(utils.convertToJSON(message=f'Party {currentParty} has been disbanded.'))
                                print(partyList)
                                broadcast(bytesToSend)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)

            #transfer party leader
            case "pleader":
                if ALLOW_PARTY:
                    if( clientHandle[address] != None #client username exists
                        and msg["handle"] in clientHandle.values()): #receiver username exists
                        currentParty = None
                        newLeaderHandle = msg["handle"]
                        newLeaderAddress = list(clientHandle.keys())[list(clientHandle.values()).index(msg["handle"])]

                        for party in partyList:
                            if address in partyList[party]["users"]:
                                currentParty = party #get current party of user
                                break
                        if currentParty == None:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: You are currently not in a party."))
                            sendData(bytesToSend, address)
                        elif newLeaderAddress not in partyList[currentParty]["users"]:
                            bytesToSend = str.encode(utils.convertToJSON(message=f'Error: {newLeaderHandle} is not in the party'))
                            sendData(bytesToSend, address)
                        elif address == partyList[currentParty]["leader"]:
                            partyList[currentParty]["leader"] = newLeaderAddress
                            bytesToSend = str.encode(utils.convertToJSON(message=f'{newLeaderHandle} is now the party leader.'))
                            receiverList = partyList[currentParty]["users"]
                            multicast(bytesToSend, receiverList)
                        else:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: Only party leaders can transfer leadership."))
                            sendData(bytesToSend, address)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)

            #get current party info
            case "pinfo":
                if ALLOW_PARTY:
                    if(clientHandle[address] != None): #client username exists
                        currentParty = None
                        for party in partyList:
                            if address in partyList[party]["users"]:
                                currentParty = party #get current party of user
                                break
                        if currentParty == None:
                            bytesToSend = str.encode(utils.convertToJSON(message="Error: You are currently not in a party."))
                        else:
                            userArray = []
                            invitedArray = []
                            for user in partyList[currentParty]["users"]:
                                userArray.append(clientHandle.get(user))
                            for user in partyList[currentParty]["invited"]:
                                invitedArray.append(clientHandle.get(user))

                            partyLeader = clientHandle[partyList[currentParty]["leader"]]
                            partyUsers =  ', '.join(userArray)
                            invitedPartyUsers =  ', '.join(invitedArray)
                            bytesToSend = str.encode(utils.convertToJSON(message=f'Party name: {currentParty} \nParty leader - {partyLeader} \nUsers: {partyUsers}\nInvited Users: {invitedPartyUsers}'))

                        sendData(bytesToSend, address)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)

            #party list
            case "partylist":
                if ALLOW_PARTY:
                    if(clientHandle[address] != None): #client username exists
                        allParties = []
                        for party in partyList:
                            allParties.append(party)
                        allParties = ', '.join(allParties)
                        bytesToSend = str.encode(utils.convertToJSON(message=f'All existing parties: \n{allParties}'))
                        sendData(bytesToSend, address)
                    else:
                        bytesToSend = str.encode(utils.convertToJSON(message="Error: Client not registered"))
                        sendData(bytesToSend, address)
                else:
                    bytesToSend = str.encode(utils.convertToJSON(message="Error: Party feature is currently disabled"))
                    sendData(bytesToSend, address)

            case _:
                bytesToSend = str.encode(utils.convertToJSON(message="Error: Cannot process unknown command"))
                sendData(bytesToSend, address)

    except ConnectionResetError:
        continue
    except Exception as e:
        print(f'Error occured - {e}')
        continue