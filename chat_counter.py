import io
import socket
import threading
import select
import os
import time
import numpy as np


def getname(message: str):
    name = ""
    i = 1
    while message[i] != '!':
        name += message[i]
        i += 1
    return name


def getmessage(message: str):
    ind = message.find("PRIVMSG")
    if ind != -1:
        ind = message.find(":", ind)
        res = message[ind + 1:len(message)-2]
    else:
        res = ""
    return res

def user():
    inp = input("please enter 'STOP' (all caps) for the bot to stop looking at the messages and start\n")
    while inp != "STOP":
        inp = input("invalid input, continuing to look at chat (respectfully of course O.O), enter 'STOP' to enter the \n")




if __name__ == '__main__':
    print("welcome to chat messages counter and giveaway program!")
    try:
        f = open('config', 'rb')
    except:
        print("since i couldn't find a config file, i'll need you to enter your twitch username and oauth token, you can get the"
              + " oauth token here https://twitchapps.com/tmi/ (please do not copy the 'oauth:' part, only copy what comes after the :")
        nick = input('please enter your twitch name\n').lower()
        password = input('and now your oauth token\n')
        f = open('config', 'wb')
        f.writelines((nick + "\n").encode('utf-8'))
        f.writelines((password + "\n").encode('utf-8'))
    else:
        nick = f.readline().decode('utf-8')
        nick = nick[0:len(nick)-1]
        password = f.readline().decode('utf-8')
        password = password[0:len(password)-1]

    f.close()
    mode = input("do you want me to watch over a [L]ive chat or look over an [E]xisting chat log?\n").upper()
    if mode == 'L':
        irc = socket.socket()
        addr = socket.gethostbyname("irc.chat.twitch.tv")
        port = 6667

        try:
            irc.connect((addr, port))
        except:
            print("failed to connect to twitch, shutting down")
            os.system('pause')
            exit(1)

        print("connected to twitch")

        irc.send(("PASS oauth:" + password + '\r\n').encode('utf-8'))
        irc.send(("NICK " + nick + '\r\n').encode('utf-8'))
        message = irc.recv(5000).decode('utf-8')
        if message.find("failed") != -1:
            print("failed to authenticate, please check your twitch name and the oauth")
            os.remove('config')
            os.system("pause")
            exit(1)
        irc.send(("JOIN #" + nick + '\r\n').encode('utf-8'))
        irc.send(("PRIVMSG #" + nick + " :chat counter is connected and is watching you O.O\r\n").encode("UTF-8"))

        userThread = threading.Thread(target=user, daemon=True)
        userThread.start()
        chatFile = open("chat log.txt", 'wb')
        msg = irc.recv(5000).decode('utf-8')
        leave = False
        timeoff = 0
        while True:
            while msg != "":
                if msg.split()[0] == "PING":
                    irc.send(("PONG " + msg.split()[1] + '\r\n').encode('utf-8'))
                else:
                    if getmessage(msg) != '':
                        for line in io.StringIO(msg).readlines():
                            written = (getname(line) + " " + str(time.time()) + " " + getmessage(line) + "\n").encode('utf-8')
                            chatFile.write(written)
                while True:
                    reeeee, _, _= select.select([irc], [], [], 0.5)
                    if reeeee:
                        msg = irc.recv(5000).decode('utf-8')
                        break
                    elif not userThread.is_alive():
                        leave = True
                        break
                if leave:
                    break
            if leave:
                break
            print("disconnected from twitch, trying to reconnect...")
            time.sleep(2 ** timeoff)
            timeoff += 1
            while timeoff != 0:
                try:
                    irc.connect((addr, port))
                except:
                    print("failed to reconnect, trying again...")
                    timeoff += 1
                    time.sleep(2 ** timeoff)
                else:
                    print('reconnected to twitch')
                    timeoff = 0
                    irc.send(("PASS oauth:" + password + '\r\n').encode('utf-8'))
                    irc.send(("NICK " + nick + '\r\n').encode('utf-8'))
                    irc.send(("JOIN #" + nick + '\r\n').encode('utf-8'))
                    msg = irc.recv(5000).decode('utf-8')
                    if msg.find("failed") != -1:
                        print("failed to authenticate, please check your twitch name and the oauth")
                        os.remove('config')
                        os.system("pause")
                        exit(1)
                    irc.send(("JOIN #" + nick + '\r\n').encode('utf-8'))
                    print("reconnected to twitch")
        chatFile.close()
        irc.send(("PRIVMSG #" + nick + " :i am no longer counting messages, please wait for the results\r\n").encode("UTF-8"))
    delay = 0.5
    choice = input("how do you want to decide the winner?\nto show the list of most talkative people enter 1\nto run a weighted raffle according to your message count " +
                   "(each message you made in chat is a ticket towards the raffle so the more you chatted the better your chances are). enter 2" +
                   "\nto run a weighted raffle according to your character count (the longer the messages you sent the higher your chances of winning). enter 3\n" +
                   "to set an a 'cool-off time' between messages to count (messages will have to have a certain time between them to count towards the score" +
                   " to counter spamming.\n the cool-off time is 0.5 by default, unless you change it) enter 4\nto exclude a certain user from "
                   "the drawing enter 5"
                   + "(those users will be saved in a text file for the next time as well, mostly for bots)\nto exit just type exit\n")
    try:
        banlist = open('banlist.txt', 'rb')
    except:
        banlist = open('banlist.txt', 'wb')
        banlist.close()
        banlist = open('banlist.txt', 'rb')

    banned = []
    for baname in banlist.readlines():
        baname.decode('utf-8')
        banned.append(baname[:-1])
    banlist.close()
    chatlog = open('chat log.txt', 'rb')
    while choice != 'exit':
        dick = {}
        if choice == '1':
            for line in chatlog.readlines():
                line = line.decode('utf-8')
                if line == '\n':
                    continue
                splitted = line.split()
                if splitted[0] in banned:
                    continue
                if splitted[0] in dick:
                    if float(dick[splitted[0]][0]) + delay <= float(splitted[1]):
                        dick[splitted[0]][0] = splitted[1]
                        dick[splitted[0]][1] += 1
                else:
                    dick[splitted[0]] = [splitted[1], 1]
            sortedDick = {k: v for k, v in sorted(dick.items(), key=lambda item: item[1][1])}
            for k in reversed(list(sortedDick)):
                print(k, sortedDick[k][1])
        elif choice == '2':
            cn = 0
            for line in chatlog.readlines():
                line = line.decode('utf-8')
                if line == '\n':
                    continue
                cn += 1
                splitted = line.split()
                if splitted[0] in banned:
                    continue
                if splitted[0] in dick:
                    if float(dick[splitted[0]][0]) + delay <= float(splitted[1]):
                        dick[splitted[0]][0] = splitted[1]
                        dick[splitted[0]][1] += 1
                else:
                    dick[splitted[0]] = [splitted[1], 1]
            draw = np.random.randint(0, cn+1)
            ind = 0
            listedick = list(dick)
            while draw> 0:
                draw -= dick[listedick[ind]][1]
                ind += 1
            try:
                irc.send(("PRIVMSG #" + nick + " :winner is: " + listedick[ind - 1] + "\r\n").encode("UTF-8"))
                print('winner is ', listedick[ind - 1])
            except:
                print('winner is ', listedick[ind - 1])
        elif choice == '3':
            cn = 0
            maxcn = 0
            for line in chatlog.readlines():
                line = line.decode('utf-8')
                if line == '\n':
                    continue
                splitted = line.split()
                if splitted[0] in banned:
                    continue
                cn = len(line) - line.find(" ", len(splitted[0]) + len(splitted[1])) - 2
                if splitted[0] in dick:
                    if float(dick[splitted[0]][0]) + delay <= float(splitted[1]):
                        dick[splitted[0]][0] = splitted[1]
                        dick[splitted[0]][1] += cn
                        maxcn += cn
                else:
                    dick[splitted[0]] = [splitted[1], cn]
                    maxcn += cn
            draw = np.random.randint(0, maxcn + 1)
            ind = 0
            listedick = list(dick)
            while draw > 0:
                draw -= dick[listedick[ind]][1]
                ind += 1
            try:
                irc.send(("PRIVMSG #" + nick + " :winner is: " + listedick[ind - 1] + "\r\n").encode("UTF-8"))
                print('winner is ', listedick[ind - 1])
            except:
                print('winner is ', listedick[ind - 1])
        elif choice == '4':
            delay = float(input('please enter the cool off time you want in seconds (e.g. 3.5 = 3 and a half seconds are required between messages)\n'))
        elif choice == '5':
            names = input("please enter the names of the users (usually bots) you want this program to ignore (you can input more then one, separate them by comas)\n")
            try:
                banlist = open('banlist.txt', 'ab')
            except:
                banlist = open('banlist.txt', 'wb')
            banlist.writelines([(mys + '\n').encode('utf-8') for mys in [s.strip() for s in names.split(',')]])
            banlist.close()
            banned.append([s.strip() for s in names.split(',')])
        else:
            print("error, couldn't find your choice, please try again")
        print('\n')
        choice = input(
            "how do you want to decide the winner?\nto show the list of most talkative people enter 1\nto run a weighted raffle according to your message count " +
            "(each message you made in chat is a ticket towards the raffle so the more you chatted the better your chances are). enter 2" +
            "\nto run a weighted raffle according to your character count (the longer the messages you sent the higher your chances of winning). enter 3\n" +
            "to set an a 'cool-off time' between messages to count (messages will have to have a certain time between them to count towards the score" +
            " to counter spamming.\n the cool-off time is 0.5 by default, unless you change it) enter 4\nto exclude a certain user from "
            "the drawing enter 5"
            + "(those users will be saved in a text file for the next time as well, mostly for bots)\nto exit just type exit\n")
        chatlog.seek(0, 0)
    print("goodbye")

