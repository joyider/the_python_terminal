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


import SocketServer
from socket import error as socketError
from thread import start_new_thread
from time import sleep

players = {}
commands = []
serverReady = False

def yell(msg):
    broadcast(msg)

def echo(msg):
    broadcast(msg)

def broadcast(msg):
    for p in players.values():
        p.send(msg)
    print msg

class Player(SocketServer.BaseRequestHandler):

    def handle(self):
        try:
            # everyone has unique name
            self.vars = {'name' : 'anonymous'}
            while players.has_key(self.vars['name']):
                self.vars['name'] = self.vars['name'] + "1"

            while True:
                data = self.read()

                if len(data) != 0:
                    pID = ord(data[0])
                    msg = data[1:]
                    self.readPacket(pID, msg)
        except socketError:
            self.disconnect()

    def disconnect(self):
        players.pop(self.vars['name'])
        self.broadcast(self.vars['name'] + " has disconnected.")

    def readPacket(self, pID, msg):
        if pID == 0:    # packet error
            print "packet error"
        elif pID == 1:  # connected with name
            name = msg
            while players.has_key(name):
                name = name + "1"
            self.vars['name'] = name
            players[self.vars['name']] = self
            self.broadcast(self.vars['name'] + " has joined!")
            self.send(self.vars['name'])
        elif pID == 2:  # broadcast message
            self.command(msg)
        else:
            print "[" + str(pID) + "] unrecognized packet: " + msg

    def command(self, cmd):
        commands.append((self, cmd))

    def read(self):
        return self.request.recv(1024).strip()

    def send(self, msg):
        self.request.send(msg)

    def broadcast(self, msg):
        for p in players.values():
            if p != self:
                p.send(msg)
        print msg

def serverInit():
    print "Setting up..."
    HOST, PORT = "", 9999

    print "Starting server..."
    server = SocketServer.ThreadingTCPServer((HOST, PORT), Player)
    print "Set up!"

    print "Serving..."
    global serverReady
    serverReady = True
    server.serve_forever()

if __name__ == "__main__":
    start_new_thread(serverInit, ())

    while not serverReady:
        sleep(0.05)

    print "Init python terminal"
    while True:
        if len(commands) != 0:
            temp = commands
            commands = []
            for (pl, cmd) in temp:
                try:
                    pl.broadcast(pl.vars['name'] + "> " + cmd)
                    exec cmd
                except Exception, e:
                    broadcast(str(e))
        sleep(0.01)
