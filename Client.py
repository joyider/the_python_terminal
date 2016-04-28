#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# the_python_terminal (c) 2016 by Andre Karlsson<andre.karlsson@protractus.se>
#
# This file is part of the_python_terminal.
#
#    the_python_terminal is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# Filename:  by: andrek
# Timesamp: 4/28/16 :: 9:19 PM

from sys import stdout, exit
from time import sleep
from socket import socket, AF_INET, SOCK_STREAM
from socket import error as socketError
from thread import start_new_thread
from thread import error as threadError
from Getch import _Getch
from pyperclip import copy
from pyperclip import paste
getch = _Getch()

HOST, PORT = "localhost", 9999
BEEP = True

# TODO: Replace exit(0) for socketErrors with something more effective.
# Right now they are not exiting because they are not being called from the
# 'main thread'
# See docs: http://docs.python.org/2/library/sys.html#sys.exit


class Client():
    """ A simple chat client """

    def __init__(self, connectionInfo):
        """ Initialize the client with connectionInfo = (HOST, PORT) """

        try:
            stdout.write("Name: ")
            name = raw_input()
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(connectionInfo)
            self.send(1, name)
            self.name = self.read()
            self.prefix = self.name + "> "
            self.enters = 0
            self.pastCommands = []
            self.pastCommandsPtr = 0
            self.newline = 0
            self.secondChar = False
            print "HELLO " + self.name + "!"
            print "You are now connected. \n"
            print "Use \"echo()\" instead of \"print\" to see outputs."
        except socketError:
            print "There was an error in connecting to the server. Please " + \
                  "check that the server is actually running!"
            exit(0)
        self.start()

    def start(self):
        """ Start the threads necessary for input and output. """
        self.cin = []
        self.cout = ""
        self.coutQ = ""
        try:
            start_new_thread(self.input, ())
            start_new_thread(self.output, ())
            self.run()
        except threadError:
            print "There was an error in creating a new thread. This is " + \
                  "probably a problem with your computer."
            exit(0)

    def run(self):
        """ Main loop for client. Keep threads running, capture user input and
        output.
        """

        stdout.write(self.prefix)
        while True:
            if len(self.cin) != 0:
                for c in self.cout:
                    stdout.write("\b \b")
                for c in self.prefix:
                    stdout.write("\b \b")
                for msg in self.cin:
                    stdout.write(msg + "\n")
                stdout.write(self.prefix)
                stdout.write(self.cout)
                self.cin = []

            if len(self.coutQ) > 0:
                temp = self.coutQ
                self.coutQ = self.coutQ[len(temp):]
                for c in temp:
                    if ord(c) == 8:
                        if len(self.cout) > 0 and self.cout[-1] != '\n':
                            stdout.write("\b \b")
                            self.cout = self.cout[0:-1]
                    elif ord(c) == 10:
                        pass
                    elif ord(c) == 13:
                        if (len(self.cout) > 0 and self.cout.strip()[-1] == ":") \
                        or (self.enters and self.cout[-1] != "\n"):
                            stdout.write("\n")
                            self.cout += "\n"
                            self.enters = True
                        else:
                            stdout.write("\n")
                            self.send(2, self.cout)
                            self.pastCommands.append(self.cout)
                            self.pastCommandsPtr = 0
                            self.cout = ""
                            stdout.write(self.prefix)
                            self.enters = False
                    elif ord(c) == 22:
                        self.coutQ += paste()
                    elif ord(c) == 3:
                        copy(self.cout)
                    elif ord(c) == 224:
                        self.secondChar = True
                    elif ord(c) == 72 and self.secondChar:
                        if self.pastCommandsPtr < len(self.pastCommands):
                            self.pastCommandsPtr += 1
                        for c in self.cout:
                            stdout.write("\b \b")
                        tempCmd = self.pastCommands[-self.pastCommandsPtr]
                        if not '\n' in tempCmd:
                            self.cout = tempCmd
                            stdout.write(self.cout)
                        self.secondChar = False
                    elif ord(c) == 80 and self.secondChar:
                        if self.pastCommandsPtr > 1:
                            self.pastCommandsPtr -= 1
                        for c in self.cout:
                            stdout.write("\b \b")
                        tempCmd = self.pastCommands[-self.pastCommandsPtr]
                        if not '\n' in tempCmd:
                            self.cout = tempCmd
                            stdout.write(self.cout)
                        stdout.write(self.cout)
                        self.secondChar = False
                    else:
                        stdout.write(c)
                        self.cout += c
                    if ord(c) != 224:
                        self.secondChar = False

            sleep(0.01)

    def input(self):
        """ Call read() and process information """
        try:
            while True:
                msgIn = self.read()
                self.cin.append(msgIn)
        except socketError:
            print "The server has disconnected. Go beat up your sysadmin."
            exit(0)

    def output(self):
        """ Read user input from termianl (single character) """
        try:
            while True:
                c = getch()
                self.coutQ += c
        except socketError:
            print "The server has disconnected. Go beat up your sysadmin."
            exit(0)

    def read(self):
        """ Read information passed from the server """
        return self.sock.recv(1024).strip()

    def send(self, pID, msg):
        """ Send information to the server """
        self.sock.sendall(chr(pID) + msg)


if __name__ == "__main__":
    Client((HOST, PORT))