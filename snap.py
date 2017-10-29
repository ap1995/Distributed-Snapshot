# -*- coding: utf-8 -*-
# Created on Thu Oct 5 14:07:10 2017

# @author: ashwini

from socket import *
from _thread import *
import json
import threading
import random
from heapq import *
import time
import sys

class Customer:
    hostname = ''
    port = 0
    s = None
    processID = 0
    replyList = []

    # Initializing Client and its attributes
    def __init__(self, ID):
        print("System running: " + ID)
        self.ID = ID
        port = configdata["customers"][ID][1]
        name = configdata["customers"][ID][2]
        self.money = configdata["customers"][ID][3]
        self.name = name
        self.port = port
        self.initiate = False
        self.snapped = False
        self.markerCount = 0
        self.processID = int(self.port) - 4000
        self.hostname = gethostname()
        self.output = open('snaps.txt', 'w')
        # self.dictionary = open('data.json', 'w')
        self.dictionary = dict()
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
            port = msg.split()[-1]
            addmoney = int(msg.split()[4])
            self.money = self.money + addmoney
            print("New Balance " + str(self.money)+ " dollars")
            if self.snapped:
                if self.dictionary[int(self.snapID)] >= 0 <2 or self.initiate:
                    addToDict = {port: [self.port, addmoney]}
                    self.dictionary[int(self.snapID)] = addToDict
                    # x = json.loads(self.dictionary)
                    # print(x)

        if "Marker" in msg:
            port = msg.split()[2]
            print(self.dictionary)
            self.dictionary[int(self.snapID)] = self.dictionary[int(self.snapID)] +1
            self.whenSnapped(int(self.snapID))

        if "Add" in msg:
            self.snapID = msg.split()[-1]
            newSnap = {int(self.snapID): self.markerCount}
            self.dictionary = newSnap
            print(json.dumps(self.dictionary))

    def awaitInput(self):
        while True:
            message = input('Enter snap to take a snapshot: ')
            if (message == 'snap'):
                self.initiate = True
                self.snapID = self.processID
                toAdd = {self.snapID: self.markerCount}
                m = "Add to dict "+ str(self.snapID)
                self.sendToAll(m)
                self.dictionary = toAdd
                # self.markerCount = self.markerCount +1
                start_new_thread(self.whenSnapped, (self.snapID,))
            else:
                print('Invalid input')

    def whenSnapped(self, snapID):

        # systemName = "C" + str(self.processID)
        self.snapped =True
        # print("Snapshot initiated by process "+str(snapID))
        if int(self.dictionary[snapID]) < 2:
            snapState = self.name + " " + str(self.money) # write to a text file
            self.output.write(snapState)
            marker = "Marker from " + str(self.port)
            # print(marker)
            self.sendToAll(marker)
            time.sleep(delay)

        if self.dictionary[snapID] ==2:
            print("Snapshot complete")
            self.output.close()
            self.dictionary[snapID] = 0

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
