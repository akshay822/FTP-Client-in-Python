import sys, socket, os

'''
Name: Akshay Desai

This program reads standard input to accept input lines that a user can use to request
three FTP operations, GET, CONNECT, and QUIT.

I split the input lines to subsequently check if each command is valid and then handle each error case accordingly
based on the specifications.

Assignment 5 Update: Combined FTPclient1 and FTPclient2 in order to build a full FTPClient. Connected this FTPClient
to requested servers using given hostnames and ports from the command and request lines.
'''

def replyparser(reply):
    '''begin ftpclient2.py'''

    #split the reply by space first
    linesplit = reply.split(" ", 1)[0:2]

    if(len(linesplit) == 2):
        if(linesplit[0].isdigit() == True):
            if(int(linesplit[0]) >= 100 and int(linesplit[0]) <= 599):

                #used strip in order to handle crlf after replytext is checked to be valid
                replytext = linesplit[1].rstrip('\r\n')

                invalidchar = 0

                #check if replytext contains only valid characters
                for i in list(replytext):
                    if(ord(i) > 127 or i == '\n' or i == '\r'):
                        invalidchar += 1

                if(invalidchar > 0):
                    return "ERROR -- reply-text"+"\r\n"


                if('\r\n' in linesplit[1]):
                    return "FTP reply "+str(linesplit[0])+" accepted. Text is: "+replytext+"\n"

                else:
                    return "ERROR -- <CRLF>"+"\r\n"

            else:
                return "ERROR -- reply-code"+"\r\n"

        else:
            return "ERROR -- reply-code"+"\r\n"
    else:
        return "ERROR -- reply-code"+"\r\n"

    '''end ftpclient2.py'''

if(len(sys.argv) == 2):
    argportnumber = sys.argv[1]
else:
    print("Too little or too many arguments")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
    print("socket creation failed")

connected = False
fileincrement = 1
for line in sys.stdin:
    sys.stdout.write(line)

    #trim trailing return characters then split by space
    linestripped = line.rstrip('\n\r\n')
    linesplit = linestripped.split(" ", 1)[0:2]

    #handle case insensitive commands
    cmdupper = linesplit[0].upper()
    if(cmdupper == "CONNECT" or cmdupper == "GET" or cmdupper == "QUIT" and ('\n' in line or '\r' in line)):

            if(cmdupper == "CONNECT"):
                if(cmdupper == "CONNECT"):

                    secondsplit = linesplit[1].rsplit(" ", 1)[0:2]

                    invalidchar = 0
                    serverhost = secondsplit[0].lstrip()

                    #create alphabetic dictionary to check against first character of serverhost
                    justalpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w',
                    'x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V',
                    'W','X','Y','Z']

                    listserverhost = list(serverhost)
                    if(listserverhost[0] not in justalpha):
                        print("ERROR -- server-host")
                        continue

                    #created alphanumeric dictionary of usable characters for all of serverhost name
                    usablechars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w',
                    'x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V',
                    'W','X','Y','Z','0','1','2','3','4','5','6','7','8','9','.']
                    for i in list(serverhost):
                        if(i not in usablechars):
                            invalidchar += 1

                    if(invalidchar > 0):
                        print("ERROR -- server-host")
                        continue

                    #check port number, if it's a valid digit then do required operations...
                    if(secondsplit[-1].isdigit() == True):
                        if(int(secondsplit[-1]) >= 0 and int(secondsplit[-1]) <= 65535):

                            if(connected == True):
                                s.close()

                            connected = True

                            print("CONNECT accepted for FTP server at host "+serverhost+" and port "+secondsplit[-1])

                            try:
                                s.connect((""+serverhost, int(secondsplit[-1])))
                            except:
                                connected = False
                                print("CONNECT failed")
                                continue

                            sys.stdout.write(replyparser(s.recv(1024).decode()))
                            s.send("USER anonymous\r\n".encode())
                            sys.stdout.write("USER anonymous\r\n")
                            sys.stdout.write(replyparser(s.recv(1024).decode()))
                            s.send("PASS guest@\r\n".encode())
                            sys.stdout.write("PASS guest@\r\n")
                            sys.stdout.write(replyparser(s.recv(1024).decode()))
                            s.send("SYST\r\n".encode())
                            sys.stdout.write("SYST\r\n")
                            sys.stdout.write(replyparser(s.recv(1024).decode()))
                            s.send("TYPE I\r\n".encode())
                            sys.stdout.write("TYPE I\r\n")
                            sys.stdout.write(replyparser(s.recv(1024).decode()))


                        else:
                            print("ERROR -- server-port")
                    else:
                        print("ERROR -- server-port")
                else:
                    print("ERROR -- request")
                    continue

            #if command was GET
            elif(cmdupper == "GET"):
                if(cmdupper == "GET"):
                    isvalid = 0
                    trailstrip = linesplit[1].lstrip()

                    #check if each character in pathname is valid
                    for i in list(trailstrip):
                        if(ord(i) > 127):
                            isvalid += 1

                    if(isvalid > 0):
                        print("ERROR -- pathname")
                        continue

                    if(connected == False):
                        print("ERROR -- expecting CONNECT")
                        continue

                    print("GET accepted for "+trailstrip)

                    try:
                        welcoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        welcoming_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        welcoming_socket.bind(("", int(argportnumber)))
                        welcoming_socket.listen(1)
                    except socket.error as err:
                        print("GET failed, FTP-data port not allocated.")
                        continue

                    #check if retr_files folder exists, if it doesn't then create it
                    if(os.path.exists(os.path.join(os.getcwd(), "retr_files")) == False):
                        os.mkdir(os.path.join(os.getcwd(), "retr_files"))

                    my_ip = socket.gethostbyname(socket.gethostname())
                    ipsplit = my_ip.split(".")

                    host_address = ipsplit[0]+","+ipsplit[1]+","+ipsplit[2]+","+ipsplit[3]

                    firstport = int(argportnumber) // 256
                    secondport = int(argportnumber) % 256

                    portstring = "PORT "+host_address+","+str(firstport)+","+str(secondport)+"\r\n"
                    sys.stdout.write("PORT "+host_address+","+str(firstport)+","+str(secondport)+"\r\n")
                    s.send(portstring.encode())
                    argportnumber = int(argportnumber) + 1
                    cat = s.recv(1024).decode()

                    if(cat[0] == "4" or cat[0] == "5"):
                        sys.stdout.write(replyparser(cat))
                        continue

                    sys.stdout.write(replyparser(cat))

                    retrstring = "RETR "+trailstrip+"\r\n"
                    sys.stdout.write("RETR "+trailstrip+"\r\n")
                    s.send(retrstring.encode())
                    dog = s.recv(1024).decode()

                    if(dog[0] == "4"  or dog[0] == "5"):
                        sys.stdout.write(replyparser(dog))
                        continue
                    else:
                        sys.stdout.write(replyparser(dog))
                        c, addr = welcoming_socket.accept()

                        file = open(os.path.join(os.path.join(os.getcwd(), "retr_files"), "file"+str(fileincrement)), "wb+")

                        totaldata=[]
                        def getfile():
                            while True:
                                minifile = c.recv(8192)
                                totaldata.append(minifile)
                                if(minifile == b""):
                                    break

                            return b"".join(totaldata)

                        filereceived = getfile()

                        file.write(filereceived)
                        file.close()
                        c.close()
                        fileincrement += 1
                        sys.stdout.write(replyparser(s.recv(1024).decode()))
                        welcoming_socket.close()
                        continue

                    welcoming_socket.close()

                    sys.stdout.write(replyparser(s.recv(1024).decode()))

                else:
                    print("ERROR -- request")

            #if command was QUIT
            elif(cmdupper == "QUIT"):
                if(cmdupper == "QUIT" and len(linesplit) == 1):
                    if(connected == False):
                        print("ERROR -- expecting CONNECT")
                        continue

                    s.send("QUIT\r\n".encode())
                    print("QUIT accepted, terminating FTP client")
                    sys.stdout.write("QUIT\r\n")
                    sys.stdout.write(replyparser(s.recv(1024).decode()))
                    s.close()
                    continue
                else:
                    print("ERROR -- request")
    else:
        print("ERROR -- request")
        continue
