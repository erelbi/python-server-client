#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import socket
import os
import sys
import threading
import redis
import psutil
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

BUFFER_SIZE = 20


root = tk.Tk()

#### database bağlantısı
mydb = mysql.connector.connect(
        host="192.168.1.182",
        user= "fm3",
        passwd="tornavida",
        database="javatar_db"
        )
###########################
sql_select_Query = "select hostname from proje"
cursor = mydb.cursor()
cursor.execute(sql_select_Query)
records = cursor.fetchall()
#######hostname listesi#######
sql_select_Query = "select hostname from proje"
cursor = mydb.cursor()
cursor.execute(sql_select_Query)
records = cursor.fetchall()
#######ip ve hostname########
ip_address = ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)),
s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
socket.SOCK_DGRAM)]][0][1]]) if l][0][0])


host_name = socket.gethostname()
###############################



root.title("Client")

text = tk.Text(master=root)
text.pack(expand=True, fill="both")

entry = tk.Entry(master=root)
entry.pack(expand=True, fill="x")

frame = tk.Frame(master=root)
frame.pack()


def buttons():
    for i in "baglan", "hostname", "yolla", "temizle", "Exit":
        b = tk.Button(master=frame, text=i)
        b.pack(side="left")
        yield b


b1, b2, b3, b4, b5 = buttons()




class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def baglan(self):
        now = str(datetime.now())[:-7]
        if self.nickname is not None:
            try:
                self.s.connect(("192.168.1.182", 9019))
                mycursor = mydb.cursor()
                sql =  " INSERT INTO proje (hostname,ip) VALUES ( %s, %s )"
                val = ( self.nickname, ip_address)
                mycursor.execute(sql,val)
                mydb.commit()
                text.insert("insert", "({}) : Baglandı.\n".format(now))

                self.s.sendall(bytes("{}".format(self.nickname).encode("utf-8")))
                self.receive()
            except ConnectionRefusedError:
                text.insert("insert", "({}) : Sunucu online.\n".format(now))
        else:
            text.insert("insert", "({}) : hostname i giriniz.\n".format(now))






    def receive(self):
        while True:
            r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
            durum = r.get("client1:durum")
            data = str(self.s.recv(1024))[2:-1]
            print (data)
            now = str(datetime.now())[:-7]
            komut = str.format(data)
            m = str('sistem musait degil')
            if durum == "müsait":

                f = str(os.popen(komut).read())

#            self.s.sendall(bytes("{}".format(self.nickname, "clientın komut çıktısı" ).encode("utf-8")))
                self.s.sendall(bytes("{}".format( f ).encode("utf-8")))
            elif durum == "müsait değil":
                        self.s.sendall(bytes("{}".format(m).encode("utf-8")))


            elif len(data) == 0:

                pass
            elif len(data) == 1:
                text.insert("insert", "({}) : {}\n".format(now, data, ))
#                text.insert((now, 'server', f ))

    def do_nothing(self):
        pass

    def hostname_giriniz(self):
        b2.configure(command=self.do_nothing)
        _frame = tk.Frame(master=root)
        _frame.pack()
        new_entry = tk.Entry(master=_frame)
        new_entry.grid(row=0, column=0)
        new_button = tk.Button(master=_frame, text="hostname i onayla")
        new_button.grid(row=1, column=0)


        def nickname_command():
            now = str(datetime.now())[:-7]
            if new_entry.get() == "":
                text.insert("insert", "({}) : hostname i girmeniz gerekmektedir.\n".format(now))
            elif any( new_entry.get() in s for s in records):
                text.insert("insert", "({}) : bu hostname sistemde kayıtlıdır.Lütfen başka hostname giriniz\n".format(now))
            else:

                self.nickname = new_entry.get()
                _frame.destroy()
                text.insert("insert", "({}) : hostname değişti yeni ismi: '{}'\n".format(now, self.nickname))
                b2.configure(command=c1.hostname_giriniz)

        new_button.configure(command=nickname_command)

    def yolla(self):
        respond = "{}: {}".format(self.nickname, str(entry.get()))
        now = str(datetime.now())[:-7]
        entry.delete("0", "end")
        try:
            self.s.sendall(bytes(respond.encode("utf-8")))
            text.insert("insert", "({}) : {}\n".format(now, respond))
        except BrokenPipeError:
            text.insert("insert", "({}) : Server a bağlantı hatası.\n".format(now))
            self.s.close()


c1 = Client()


def baglan():
    t1 = threading.Thread(target=c1.baglan)
    t1.start()


def yolla():
    t2 = threading.Thread(target=c1.yolla)
    t2.start()




def temizle():
    text.delete("1.0", "end")


def destroy():
    root.destroy()


if __name__ == "__main__":
    b1.configure(command=baglan)
    b2.configure(command=c1.hostname_giriniz)
    b3.configure(command=yolla)
    b4.configure(command=temizle)
    b5.configure(command=destroy)
    t0 = threading.Thread(target=root.mainloop)
    t0.run()
