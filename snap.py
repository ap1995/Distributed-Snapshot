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
        self.snapinProgress = False
        self.s = socket(AF_INET, SOCK_STREAM)
        print(self.name + ", $" + str(self.money))

        start_new_thread(self.startListening, ())
        start_new_thread(self.awaitInput, ())
        time.sleep(5)
        start_new_thread(self.sendMoney, ())
        while True:
            pass

    def receiveMessages(self, conn, addr):
        msg = conn.recv(1024).decode()
        print(msg)

        if "Money" in msg:
            senderport = msg.split()[2]
            receiverport = msg.split()[-1]
            addmoney = int(msg.split()[4])
            self.money = self.money + addmoney
            print("New Balance " + str(self.money)+ " dollars")
            for i in self.markerReceived:
                if self.snapinProgress and not self.markerReceived[i][receiverport]: # and if not received marker in that channel
                    addToDict = {senderport: [receiverport, addmoney]}
                    self.channelState.update({i: addToDict})
                    self.output.write(self.channelState)
                    # print(self.channelState)

        if "Marker" in msg:
            port = msg.split()[2]
            snapID = int(msg.split()[-1])
            self.markerReceived[snapID].update({port:True})
            # self.markerReceived[snapID][port]= True
            self.snapinProgress =True
            print(self.markerReceived)
            if snapID != self.snapID:
                self.whenSnapped(snapID)
            self.checkifComplete(snapID)

        if "Add" in msg:
            snapID = int(msg.split()[3])
            newSnap = {int(snapID): {}}
            self.markerReceived.update(newSnap)
            print(json.dumps(self.markerReceived))

    def awaitInput(self):
        # define markerReceived dictionary with false values
        while True:
            message = input('Enter snap to take a snapshot: ')
            if (message == 'snap'):
                self.snapinProgress = True
                self.markerCount = 0
                toAdd = {self.snapID: {}}
                m = "Add to dict "+ str(self.snapID)
                self.sendToAll(m)
                self.markerReceived = toAdd
                self.whenSnapped(self.snapID)
            else:
                print('Invalid input')

    def whenSnapped(self, snapID):

        # systemName = "C" + str(self.processID)
        # print("Snapshot initiated by process "+str(snapID))
        markerCount = 0
        for i in self.markerReceived[snapID]:
            # print(self.markerReceived[snapID][i])
            if (self.markerReceived[snapID][i] == True):
                markerCount += 1

        if markerCount >=0 and markerCount <2:
            snapState = self.name + " " + str(self.money) # write to a text file
            # print(self.markerReceived[snapID])
            self.output = open('snaps_'+str(self.processID)+'.txt', 'a+')
            self.output.write(snapState)
            marker = "Marker from " + str(self.port) + " "+ str(snapID)
            # print(marker)
            self.sendToAll(marker)
            time.sleep(delay)

    def checkifComplete(self, snapID):
        markerCount = 0
        for i in self.markerReceived[snapID]:
            print(self.markerReceived[snapID][i])
            if (self.markerReceived[snapID][i] == True):
                markerCount += 1
        if markerCount ==2: #Check for 2 Trues
            print("Snapshot complete")
            self.snapinProgress = False
            self.output.close()
            # self.markerReceived.pop(snapID)

            # outfile = 'snaps.txt'
            # destination = open(outfile, 'w')
            # shutil.copyfileobj(open('snaps_1.txt', 'rb'), destination)
            # shutil.copyfileobj(open('snaps_2.txt', 'rb'), destination)
            # shutil.copyfileobj(open('snaps_3.txt', 'rb'), destination)
            # destination.close()

        ## Print snapshot
        # print(snapState)
        # Print everyone else's balances and money on the fly


    def sendMoney(self):
        ## select random money to send with 0.2 probability
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
            time.sleep(10)
        else:
            time.sleep(10)

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
                time.sleep(delay)
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
