# -*- coding: utf-8 -*-
# Created on Thu Oct 5 14:07:10 2017

# @author: ashwini

from socket import *
from _thread import *
import json
import threading
import random
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
        self.markerCount = 0
        self.processID = int(self.port) - 4000
        self.hostname = gethostname()
        # self.replyList = []
        self.output = open('snaps.txt', 'w')
        self.dictionary = open('data.json', 'w')

        self.dictionary = {}
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
            port = msg.split()[3]
            addmoney = int(msg.split()[4])
            self.money = self.money + addmoney
            print("New Balance " + str(self.money))
            if self.markerCount >=0 <2 or self.initiate:
                addToDict = {port: [self.port, addmoney]}
                self.dictionary = json.dumps(addToDict, self.dictionary)
                x = json.loads(self.dictionary)
                print(x)
                
        if "Marker" in msg:
            port = msg.split()[2]
            self.markerCount = self.markerCount +1
            self.whenSnapped()

    def awaitInput(self):
        while True:
            message = input('Enter snap to take a snapshot: ')
            if (message == 'snap'):
                self.initiate = True
                # self.markerCount = self.markerCount +1
                self.whensnap = threading.Thread(target = self.whenSnapped)
                # start_new_thread(self.whenSnapped, ())
                if self.markerCount >= 0 < 2:
                    self.whensnap.run()
                else:
                    self.whensnap._stop()
                    print("Snapshot complete")
                    print(json.load(self.dictionary))
                    self.output.close()
                    self.markerCount = 0
            else:
                print('Invalid input')

    def whenSnapped(self):

        systemName = "C" + str(self.processID)
        # if self.markerCount < 2:
        snapState = self.name + " " + str(self.money) # write to a text file
        self.output.write(snapState)
        marker = "Marker from " + str(self.port)
        # print(marker)
        self.sendToAll(marker)
        time.sleep(delay)

        # if self.markerCount ==2:

        ## Print snapshot
        # Print everyone else's balances and money on the fly


    def sendMoney(self):
        ## select random money to send with 0.2 probability
        i = random.randrange(0, 10)
        if (i <= 2):
            sendmoney = random.randint(0, 1000)
            print("Current Balance " + str(self.money))
            self.money = self.money - sendmoney
            print("New Balance " + str(self.money))
            c = ["C1", "C2", "C3"]
            # print(c)
            c.remove(self.ID)
            # print(c)
            receiver = random.choice(c)
            receiverport = configdata["customers"][receiver][1]
            moneymessage = "Money sent from " + str(self.port) + " " + str(sendmoney) + " to customer at" + str(receiverport)
            self.sendMessage(receiverport, moneymessage)
            time.sleep(10)
        # else:
        #     time.sleep(10)

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
