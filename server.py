#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from datetime import datetime
import socket
import threading
import freeport
from psutil import process_iter
from signal import SIGTERM
import redis
redis_host = "192.168.1.182"
redis_port = 1992
redis_password = ""
root = tk.Tk()
root.title("Server")

text = tk.Text(master=root)
text.pack(expand=True, fill="both")

entry = tk.Entry(master=root)
entry.pack(expand=True, fill="x")

frame = tk.Frame(master=root)
frame.pack()


def buttons():
    for i in "Baglan", "Yolla", "temizle", "Exit","kopart","Client Listele":
        b = tk.Button(master=frame, text=i)
        b.pack(side="left")
        yield b


b1, b2, b3, b4, b5, b6, = buttons()


class Server:
    clients = []

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def baglan(self):
        self.s.bind(("",9019 ))
        self.s.listen(10)
        now = str(datetime.now())[:-7]
        text.insert("insert", "({}) : baglandı.\n".format(now))
        self.condition()

    def accept(self):
        c, addr = self.s.accept()
        self.clients.append(c)
        data = c.recv(1024)
        text.insert("insert", "({}) : {} sunucuya baglandı.\n".format(str(datetime.now())[:-7], str(data)[1:]))

    def receive(self):
        for i in self.clients:

            def f():
                data = str(i.recv(1024))[2:-1]
                now = str(datetime.now())[:-7]
                if len(data) == 0:
                    pass
                else:
                    text.insert("insert", "({}) : {}\n".format(now, data))

            t1_2_1 = threading.Thread(target=f)
            t1_2_1.start()

    def condition(self):
        while True:
            t1_1 = threading.Thread(target=self.accept)
            t1_1.daemon = True
            t1_1.start()
            t1_1.join(1)
            t1_2 = threading.Thread(target=self.receive)
            t1_2.daemon = True
            t1_2.start()
            t1_2.join(1)
    def yolla(self):
        respond = format(str(entry.get()))
        now = str(datetime.now())[:-7]
        entry.delete("0", "end")
        try:
            for i in self.clients:
                i.sendall(bytes(respond.encode("utf-8")))
                text.insert("insert", "({}) : {}\n".format(now, respond))
        except BrokenPipeError:
                text.insert("insert", "({}) : Client has been disconnected.\n".format(now))


    def kopart(self):
        for proc in process_iter():
            for conns in proc.connections(kind='inet'):
                if conns.laddr.port == 9025:
                    proc.send_signal(SIGTERM)

s1 = Server()


def baglan():
    t1 = threading.Thread(target=s1.baglan)
    t1.start()


def yolla():
    t2 = threading.Thread(target=s1.yolla)
    t2.start()


def temizle():
    text.delete("1.0", "end")

def kopart():
    t3 = threading.Thread(target=s1.kopart)
    t3.start()


def destroy():
    root.destroy()
    exit()


if __name__ == "__main__":
    b1.configure(command=baglan)
    b2.configure(command=yolla)
    b3.configure(command=temizle)
    b4.configure(command=destroy)
    b5.configure(command=kopart)
    t0 = threading.Thread(target=root.mainloop)
    t0.run()
