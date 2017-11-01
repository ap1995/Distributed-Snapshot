# -*- coding: utf-8 -*-
# Created on Thu Oct 5 14:07:10 2017

# @author: ashwini

from socket import *
from _thread import *
import json
import threading
import shutil
import random
from heapq import *
import time
import sys

class Customer:

    # Initializing Client and its attributes
    def __init__(self, ID):
        print("System running: " + ID)
        self.ID = ID
        self.port = configdata["customers"][ID][1]
        self.name = configdata["customers"][ID][2]
        self.money = configdata["customers"][ID][3]
        self.processID = int(self.port) - 4000
        self.hostname = gethostname()
        self.snapID = self.processID
        self.channelState = dict()
        self.markerReceived = dict()
        self.snapInitiator = 0
        self.snapinProgress = False
        self.s = socket(AF_INET, SOCK_STREAM)
        print(self.name + ", $" + str(self.money))
        self.output = open('outputfiles/snaps_' + str(self.processID) + '.txt', 'a+')
        # self.channelOutput = open('channels.txt', 'w+')
        start_new_thread(self.startListening, ())
        start_new_thread(self.awaitInput, ())
        time.sleep(delay)
        start_new_thread(self.sendMoney, ())
        while True:
            pass

    def receiveMessages(self, conn, addr):
        msg = conn.recv(1024).decode()
        print(msg)

        if "Money" in msg:
            senderport = int(msg.split()[3])
            receiverport = int(msg.split()[-1])
            addmoney = int(msg.split()[4])
            time.sleep(delay)
            for i in self.markerReceived:
                try: ## only prints channel state for one money transaction
                    if self.snapinProgress and not self.markerReceived[i][receiverport]: # and if not received marker in that channel
                        addToDict = {senderport: [receiverport, addmoney]}
                        self.channelState.update({self.snapInitiator: addToDict})
                        self.channelOutput = open('outputfiles/channels_'+str(self.snapID)+'.txt', 'a')
                        channelString = ""
                        for k in self.channelState[i].keys():
                            naam = "C" + str(k - 4000)
                            rec = "C" + str(int(self.channelState[i][k][0]) - 4000)
                            channelString = "Snapshot " + str(self.snapInitiator) + ": " + configdata["customers"][naam][2] + " sent " + str(self.channelState[i][k][1]) + " dollars to " + str(
                                configdata["customers"][rec][2]) + "\n"
                            # channelString = "Snapshot " + str(self.snapInitiator) + ": " + str(k) + " sent " + str(self.channelState[i][k][1]) + " dollars to " + str(self.channelState[i][k][0]) + "\n"
                        print(channelString)
                        print(self.channelState)
                        self.channelOutput.write(channelString)
                        self.channelOutput.close()
                except KeyError:
                    pass
            time.sleep(delay)
            self.money = self.money + addmoney
            print("Money Received \n")
            print("New Balance " + str(self.money) + " dollars")

        if "Marker" in msg:
            # time.sleep(delay)
            port = int(msg.split()[2])
            snapID = int(msg.split()[-1])
            # self.markerReceived[snapID].update({port:True}) #################
            self.markerReceived[snapID][port]= True
            # self.snapinProgress =True
            print(self.markerReceived)
            if snapID != self.snapID:
                self.whenSnapped(snapID)
            self.checkifComplete(snapID)

        if "Snap" in msg:
            self.snapInitiator = int(msg.split()[-1])
            self.snapinProgress =True
            time.sleep(delay)

    def awaitInput(self):
        # define markerReceived dictionary with false values
        self.markerReceived.update({1: {4002:False, 4003:False}, 2: {4001:False, 4003:False}, 3: {4001:False, 4002:False}})
        while True:
            message = input('Enter snap to take a snapshot: ')
            if (message == 'snap'):
                self.snapinProgress = True
                self.markerCount = 0
                self.snapInitiator = self.snapID
                # toAdd = {int(self.snapID): {}}
                # m = "Add to dict "+ str(self.snapID)
                m = "Snap started by " + str(self.snapInitiator)
                self.sendToAll(m)
                # self.markerReceived = toAdd
                self.whenSnapped(self.snapID)
            else:
                print('Invalid input')

    def whenSnapped(self, snapID):
        # systemName = "C" + str(self.processID)
        markerCount = 0
        for i in self.markerReceived[snapID]:
            # print(self.markerReceived[snapID][i])
            if (self.markerReceived[snapID][i] == True):
                markerCount += 1
        # time.sleep(delay)
        if markerCount >=0 and markerCount <2:
            snapState = "Snapshot " + str(snapID) + ": " + self.name + " has " + str(self.money) + " dollars."+"\n" # write to a text file
            # print(self.markerReceived[snapID])
            self.output = open('outputfiles/snaps_' + str(self.processID) + '.txt', 'a')
            self.output.write(snapState)
            marker = "Marker from " + str(self.port) + " for snapshot initiated by Customer "+ str(snapID)
            time.sleep(delay)
            self.sendToAll(marker)


    def checkifComplete(self, snapID):
        markerCount = 0
        for i in self.markerReceived[snapID]:
            # print(self.markerReceived[snapID][i])
            if (self.markerReceived[snapID][i] == True):
                markerCount += 1
        if markerCount ==2: #Check for 2 Trues
            print("Snapshot complete")
            self.snapinProgress = False
            try:
                self.output.close()
            except ValueError:
                pass

            for i in self.markerReceived[snapID]:
                self.markerReceived[snapID][i] = False
            # make everything false

            outfile = 'snaps.txt'
            destination = open(outfile, 'wb')
            shutil.copyfileobj(open('outputfiles/snaps_1.txt', 'rb'), destination)
            shutil.copyfileobj(open('outputfiles/snaps_2.txt', 'rb'), destination)
            shutil.copyfileobj(open('outputfiles/snaps_3.txt', 'rb'), destination)
            shutil.copyfileobj(open('outputfiles/channels_1.txt', 'rb'), destination)
            shutil.copyfileobj(open('outputfiles/channels_2.txt', 'rb'), destination)
            shutil.copyfileobj(open('outputfiles/channels_3.txt', 'rb'), destination)
            destination.close()
            #Print snapshot

    def sendMoney(self):
        ## select random money to send with 0.2 probability
        # while True:
        i = random.randrange(0, 10)
        if (i <= 2):
            sendmoney = random.randint(0, 1000)
            print("Current Balance " + str(self.money) + " dollars")
            self.money = self.money - sendmoney
            print("New Balance " + str(self.money)+ " dollars")
            c = ["C1", "C2", "C3"]
            c.remove(self.ID)
            receiver = random.choice(c)
            receiverport = configdata["customers"][receiver][1]
            moneymessage = "Money sent from " + str(self.port) + " " + str(sendmoney) + " dollars to customer at " + str(receiverport)
            self.sendMessage(receiverport, moneymessage)
            time.sleep(delay)
            # else:
            #     time.sleep(delay)

    def startListening(self):
        try:
            self.s.bind((self.hostname, int(self.port)))
            self.s.listen(3)
            print("server started on port " + str(self.port))
            while True:
                c, addr = self.s.accept()
                conn = c
                print('Got connection from')
                print(addr)
                start_new_thread(self.receiveMessages, (conn, addr))  # connection dictionary
        except(gaierror):
            print('There was an error connecting to the host')
            self.s.close()
            sys.exit()

    def sendMessage(self, port, message):
        rSocket = socket(AF_INET, SOCK_STREAM)
        rSocket.connect((gethostname(), int(port)))
        print(message)
        rSocket.send(message.encode())
        rSocket.close()

    # To send messages to everyone
    def sendToAll(self, message):
        for i in configdata["customers"]:
            if (configdata["customers"][i][1] == self.port):  ## To not send to yourself
                continue
            else:
                cSocket = socket(AF_INET, SOCK_STREAM)
                ip, port = configdata["customers"][i][0], configdata["customers"][i][1]
                port = int(port)
                cSocket.connect((gethostname(), port))
                print('Connected to port number ' + configdata["customers"][i][1])
                cSocket.send(message.encode())
                # time.sleep(delay)
                print('Message sent to customer at port ' + str(port))
                cSocket.close()

    def closeSocket(self):
        self.s.close()


######## MAIN #########

with open('config.json') as configfile:
    configdata = json.load(configfile)

delay = configdata["delay"]

ID = sys.argv[1]
c = Customer(ID)
