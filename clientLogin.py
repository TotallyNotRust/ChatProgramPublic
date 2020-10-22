from tkinter import *
import socket
import json
import threading


################################################################################################
################################################################################################

ip = '10.11.5.6' # <--- IP OF SERVER HERE
port = 5000

Adress = (ip, port)
##############################################################################################
################################################################################################


def listener(client):
    global root
    while True:
        root.update()
        client.setblocking(0)
        try:
            msg = client.recv(1024)
        except:
            continue
        msg = json.loads(msg)
        print(f"recieved message: {msg}")
        if not msg["message"] == "Success":
            children = mainFrame.winfo_children()
            children[0].config(state=NORMAL)
            children[0].insert(END, msg["username"] + ": " +  msg["message"] + "\n")
            children[0].config(state=DISABLED)


def send(token):
    children = mainFrame.winfo_children()
    print(children)

    message = children[1]
    messages = children[0]

    message.focus_set()
    messageT = message.get()
    if not messageT == "":
        message.delete(0, 'end')

        msg = {}
        msg["type"] = "msg"
        msg["username"] = usernameT
        msg["message"] = messageT
        msg["token"] = token
        msg["ip"] = socket.gethostbyname(socket.gethostname())

        msg = json.dumps(msg)       

        print(msg)
        client.send(bytes(msg, ("utf-8")))

def update(root):
    while True:
        root.update()

def messaging(token, client, root2):
    global mainFrame
    global root
    root.destroy()
    root2.destroy()

    root = Tk()
    root.resizable(False, False)
    root.title("Message")



    mainFrame = Frame(root, height=1000, width=1000, bg="DeepSkyBlue4")
    mainFrame.pack()

    Text(mainFrame, width=40, height=11, state=DISABLED, font=("Courier", 23)).place(relx=0.5, rely=0.4, anchor=CENTER)

    Entry(mainFrame, width=25, font=("Courier", 23)).place(relx=0.405, rely=0.65, anchor=CENTER)

    Button(mainFrame, text="Send", font=("Courier", 14), width=10, command=lambda: send(token)).place(relx=0.73, rely=0.65, anchor=CENTER)

    print("Before thread")

    threading.Thread(target=listener(client)).start()

    print("After thread")


def connect():
    global client
    client = socket.socket()
    try:
        client.connect(Adress)
    except Exception as error:
        print(error)
    return client


def loginRegister(Type, username, password, root2):
    global usernameT
    if __name__ == "__main__":
        client = connect()

        data = {}
        username.focus_set()
        usernameT = username.get()
        username.delete(0, 'end')

        password.focus_set()
        passwordT = password.get()
        password.delete(0, 'end')

        data["type"] = Type
        data["username"] = usernameT
        data["password"] = passwordT

        print("ok")

        data = json.dumps(data)

        print(data)

        client.send(bytes(data, ("utf-8")))

        msg = client.recv(1024)
        msg = msg.decode("utf-8")
        print(msg)
        if not msg == None:
            msg = json.loads(msg)
            if msg["message"] == "Success":
                print("Success")
                token = msg["token"]
                print(token)
                messaging(token, client, root2)
            elif msg["message"] == "No such user":
                print("No such user")
                #client.close()
            elif msg["message"] == "User exists":
                print("User already exists")
                #client.close()
            else:
                print(msg["message"])
                #client.close()

    else:
        print("Please run the file directly!")
        root.destroy()
        root2.destroy()

################################################################################################
################################################################################################


root = Tk()


root.title("Front page")

register = Button(root, text="Register", width=20, command=lambda: main("Register"))
login = Button(root, text="Login", width=20, command=lambda: main("Login"))
label = Label(root, text="Do you want to:")
label.grid(row=0, column=0, sticky=NSEW, columnspan=4)
register.grid(row=1, column=0, sticky=NSEW, columnspan=4)
login.grid(row=2, column=0, sticky=NSEW, columnspan=4)


def main(Type):

    root2 = Tk()

    root2.geometry("250x90")
    root2.title(Type)

    username = Entry(root2)
    password = Entry(root2, show="*")
    Label(root2, text="Username").grid(row=0, column=0)
    Label(root2, text="Password").grid(row=1, column=0)
    username.grid(row=0, column=1)
    password.grid(row=1, column=1)
    Button(root2, text="Next", command=lambda: loginRegister(Type, username, password, root2)).grid(row=2, column=1, columnspan=1)


root.mainloop()
