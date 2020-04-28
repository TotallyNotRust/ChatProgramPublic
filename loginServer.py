import socket
import json
import hashlib
import binascii
import os
import random
import string
import threading
import sqlite3 as sql


def hashPassword(password):
    hashed = hashlib.sha256(password.encode("utf-8"))
    textHashed = hashed.hexdigest()
    return textHashed


def verify_password(stored_password, provided_password):

    hashed = hashlib.sha256(provided_password.encode("utf-8"))
    print(hashed.hexdigest(), stored_password)
    return stored_password == hashed.hexdigest()


conn = sql.connect(":memory:")
c = conn.cursor()

c.execute(" create table users (username, password) ")
c.execute(" insert into users values (?, ?) ", ("username", hashPassword("password")))


Address = ('', 5000)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(Address)
server.listen(5)
server.setblocking(1)
socket.setdefaulttimeout(1)

clients = []
lastusers = ""


def letters():
    allLetters = string.ascii_letters + string.digits
    listLetters = []
    for char in allLetters:
        listLetters.append(char)
    return listLetters


clients = {}

#Receive message


def recvMsg():
    global clients
    while True:
        try:
            for i in clients:
                try:
                    msg = i.recv(1024)
                    msg = msg.decode("utf-8")
                    try:
                        msg = json.loads(msg)
                        if msg["type"] == "msg":
                            print(msg)
                            if msg["token"] == clients[i]:
                                print(msg["message"])
                                print(clients[i])
                                del msg["token"]
                                msg = json.dumps(msg)
                                for x in clients:
                                    x.send(bytes(msg, ("utf-8")))
                            else:
                                print(clients)
                    except Exception as e:
                        print(e)
                except Exception as e:
                    continue
                continue
        except Exception as e:
            continue


tempClients = {}

thread = threading.Thread(target=recvMsg)


while True:
    try:
        thread.start()
    except:
        pass
    print("Awaiting connection")
    try:
        Addr, client = server.accept()

        print(f"Got request from {client}")
        msg = Addr.recv(1024)

        if not msg.decode("utf-8") == None:
            msg = msg.decode("utf-8")
            msg = json.loads(msg)
            if not msg["type"] == "msg":
                username = msg["username"]
                password = msg["password"]
            if msg["type"] == "Login":
                print("Logging in user")
                c.execute(" select * from users where username = ?", (username, ))
                users = c.fetchone()
                print(users)
                if not users == (None):
                    for i in users:
                        passwordFromDB = users[1]
                        print(passwordFromDB + "|" + password)
                        if verify_password(passwordFromDB, password):

                            reply = {}
                            reply["message"] = "Success"
                            token = ""
                            for i in range(8):
                                token = token + str(random.choice(letters()))
                            print("TOKEN", token)
                            hashtoken = hashPassword(token)
                            print(hashtoken)
                            reply["token"] = hashtoken
                            reply = json.dumps(reply)
                            Addr.send(bytes(reply, ("utf-8")))
                            print(
                                f"{client} successfully logged in to user {username} | {password}")
                            print(hashtoken)
                            clients[Addr] = hashtoken
                            break
                        else:
                            reply = {}
                            reply["message"] = "No such user"
                            reply = json.dumps(reply)
                            Addr.send(bytes(reply, ("utf-8")))
                            print(
                                f"{client} tried to connect to user {username} | {password} but failed")
                else:
                    reply = {}
                    reply["message"] = "No such user"
                    reply = json.dumps(reply)
                    Addr.send(bytes(reply, ("utf-8")))
                    print(
                        f"{client} tried to connect to user {username} | {password} but failed")

            # If the user tries to register a new user
            elif msg["type"] == "Register":
                print("Registering new user")
                c.execute(
                    " select * from users where username = ? and password = ? ", (username, password))
                responce = c.fetchone()
                if responce == None:
                    if password:
                        reply = {}
                        reply["message"] = "Success"
                        token = ""
                        for i in range(8):
                            token = token + str(random.choice(letters()))
                        hashtoken = hashPassword(token)
                        print(hashtoken)
                        reply["token"] = hashtoken
                        reply = json.dumps(reply)
                        Addr.send(bytes(reply, ("utf-8")))
                        c.execute(" insert into users values (?, ?) ",
                                (username, hashPassword(password)))
                        print(
                            f"Created new user {username} | {password} for {client}")
                        conn.commit()
                        print(hashtoken)
                        clients[Addr] = hashtoken
                else:
                    reply = {}
                    reply["message"] = "User exists"
                    reply = json.dumps(reply)
                    Addr.send(bytes(reply, ("utf-8")))
                    print(
                        f"{client} tried to create {username} | {password}, but it already exists")

        currentusers = c.fetchone()
        if currentusers != lastusers:
            lastusers = currentusers
            print(lastusers)

    except socket.timeout:
        pass
    except:
        raise
