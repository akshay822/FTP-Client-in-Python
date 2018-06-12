import sys, os, shutil, socket

'''
Name: Akshay Desai

This program is to parse FTP commands and provide output as to whether the command is valid based
on general given FTP command constraints.
I solve this problem by looping through the commands and parsing them individually as to whether they are valid.
To handle the CRLF intricacies I checked whether the input contains the '\r\n' tag and parsed it from there.

Assignment 2 Update: Fixed HW1 errors. Added PORT and RETR commands. Changed all print outputs to valid FTP replies, and added
server ready output

Assignment 5 Update: Added functionality to actually connect with a user and process the user's commmands.
'''


if(len(sys.argv) == 2):
    argportnumber = sys.argv[1]
else:
    print("Too little or too many arguments")

server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("", int(argportnumber)))
server_socket.listen(1)

while True:

    # Establish connection with client.
    c, addr = server_socket.accept()

    # send a welcome message to the client.
    c.send("220 COMP 431 FTP server ready.\r\n".encode())

    loggedin = False

    validvariable = 0
    validcommands = ["root"]

    sys.stdout.write("220 COMP 431 FTP server ready.\r\n")

    #loop through the commands
    gotquit=False
    while True:
        data=c.recv(4096).decode()
        for line in data.splitlines(keepends=True):
            if '\r\n' in line:

                #for Windows 10 FTP client users
                if(line[:4] == "OPTS"):
                    sys.stdout.write("202 UTF8 mode is always enabled. No need to send this command.\r\n")
                    c.send("202 UTF8 mode is always enabled. No need to send this command.\r\n".encode())
                    continue

                #just in case someone wants to use \r\n as part of their username or password
                howmanycrlfs = line.count('\r\n')

                splitnewline = line.split("\r\n", howmanycrlfs)[0:2]
                print(splitnewline[0], end="\r\n")

                if(len(splitnewline[0]) == 4 or len(splitnewline[0]) == 3):
                    if(splitnewline[0] != "USER" and splitnewline[0] != "PASS" and splitnewline[0] != "SYST" and splitnewline[0] != "TYPE"
                        and splitnewline[0] != "QUIT" and splitnewline[0] != "NOOP" and splitnewline[0] != "PORT" and splitnewline[0] != "RETR"):
                        sys.stdout.write("502 Command not implemented.\r\n")
                        c.send("502 Command not implemented.\r\n".encode())
                        continue

                #if there is no space, there is no parameter or the command is invalid
                if " " not in splitnewline[0] and len(splitnewline[0]) != 4:
                    #print("ERROR -- command")
                    sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                    c.send("500 Syntax error, command unrecognized.\r\n".encode())
                    continue

                #if command is valid...
                if(len(splitnewline[0]) == 4):
                    upperinput = splitnewline[0].upper()

                    if upperinput != "SYST" and upperinput != "NOOP" and upperinput != "QUIT":
                        sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                        c.send("500 Syntax error, command unrecognized.\r\n".encode())
                        continue
                    else:
                        if(upperinput == "QUIT"):
                            gotquit=True
                            sys.stdout.write("221 Goodbye.\r\n")
                            c.send("221 Goodbye.\r\n".encode())
                            c.close()
                            break

                        if(loggedin == False):
                            sys.stdout.write("530 Not logged in.\r\n")
                            c.send("530 Not logged in.\r\n".encode())
                            continue

                        if(upperinput == "SYST"):
                            if(validcommands[validvariable] == "USER" or validcommands[validvariable] == "PORT"):
                                sys.stdout.write("503 Bad sequence of commands.\r\n")
                                c.send("503 Bad sequence of commands.\r\n".encode())
                                continue

                            sys.stdout.write("215 UNIX Type: L8.\r\n")
                            c.send("215 UNIX Type: L8.\r\n".encode())
                            validcommands.append("SYST")
                            validvariable += 1
                            continue

                        if(upperinput == "NOOP"):
                            if(validcommands[validvariable] == "USER" or validcommands[validvariable] == "PORT"):
                                sys.stdout.write("503 Bad sequence of commands.\r\n")
                                c.send("503 Bad sequence of commands.\r\n".encode())
                                continue

                            sys.stdout.write("200 Command OK.\r\n")
                            c.send("200 Command OK.\r\n".encode())
                            validcommands.append("NOOP")
                            validvariable += 1
                            continue


                #split command by first space
                inputsplit = splitnewline[0].split(" ", 1)[0:2]

                firstupperinput = inputsplit[0].upper()

                #check valid commands
                if(firstupperinput == "SYST" or firstupperinput == "NOOP" or firstupperinput == "QUIT"):
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    c.send("501 Syntax error in parameter.\r\n".encode())
                    continue

                if(firstupperinput == "USER" or firstupperinput == "PASS" or firstupperinput == "TYPE"
                 or firstupperinput == "PORT" or firstupperinput == "RETR"):
                    if(firstupperinput == "USER" or firstupperinput == "PASS"):
                        if(firstupperinput == "USER"):
                            if(validcommands[validvariable] == "PORT"):
                                sys.stdout.write("503 Bad sequence of commands.\r\n")
                                c.send("503 Bad sequence of commands.\r\n".encode())
                                continue

                            strlist = list(inputsplit[1])
                            stringlength = len(inputsplit[1])
                            isvalid = 0

                            if(stringlength == 0):
                                sys.stdout.write("501 Syntax error in parameter.\r\n")
                                c.send("501 Syntax error in parameter.\r\n".encode())
                                continue

                            if(inputsplit[1] == " "*stringlength):
                                sys.stdout.write("501 Syntax error in parameter.\r\n")
                                c.send("501 Syntax error in parameter.\r\n".encode())
                                continue

                            newinputstring = inputsplit[1].lstrip()
                            newstringlength = len(newinputstring)

                            #after trimming leading whitespace if there is any
                            #loop through each character in the username to determine if byte value is >127
                            for i in range(newstringlength):
                                asciivalue = ord(strlist[i])
                                if(asciivalue > 127):
                                    isvalid += 1
                                else:
                                    isvalid += 0

                            if(isvalid > 0):
                                sys.stdout.write("501 Syntax error in parameter.\r\n")
                                c.send("501 Syntax error in parameter.\r\n".encode())
                            else:
                                sys.stdout.write("331 Guest access OK, send password.\r\n")
                                c.send("331 Guest access OK, send password.\r\n".encode())
                                validcommands.append("USER")
                                validvariable += 1

                        else:
                            if(validcommands[validvariable] == "USER"):
                                strlist = list(inputsplit[1])
                                stringlength = len(inputsplit[1])
                                isvalid = 0

                                if(stringlength == 0):
                                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                                    c.send("501 Syntax error in parameter.\r\n".encode())
                                    continue

                                if(inputsplit[1] == " "*stringlength):
                                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                                    c.send("501 Syntax error in parameter.\r\n".encode())
                                    continue

                                newinputstring = inputsplit[1].lstrip()
                                newstringlength = len(newinputstring)

                                #after trimming leading whitespace if there is any
                                #loop through each character in the password to determine if byte value is >127
                                for i in range(newstringlength):
                                    asciivalue = ord(strlist[i])
                                    if(asciivalue > 127):
                                        isvalid += 1
                                    else:
                                        isvalid += 0

                                if(isvalid > 0):
                                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                                    c.send("501 Syntax error in parameter.\r\n".encode())

                                else:
                                    c.send("230 Guest login OK.\r\n".encode())
                                    sys.stdout.write("230 Guest login OK.\r\n")
                                    validcommands.append("PASS")
                                    validvariable += 1
                                    loggedin = True;

                            else:
                                sys.stdout.write("503 Bad sequence of commands.\r\n")
                                c.send("503 Bad sequence of commands.\r\n".encode())

                    if(firstupperinput == "TYPE"):
                        if(inputsplit[1] == "A"):
                            if(loggedin == False):
                                sys.stdout.write("530 Not logged in.\r\n")
                                c.send("530 Not logged in.\r\n".encode())
                                continue

                            if(validcommands[validvariable] == "USER" or validcommands[validvariable] == "PORT"):
                                sys.stdout.write("503 Bad sequence of commands.\r\n")
                                c.send("503 Bad sequence of commands.\r\n".encode())
                                continue

                            sys.stdout.write("200 Type set to A.\r\n")
                            c.send("200 Type set to A.\r\n".encode())
                            validcommands.append("TYPEA")
                            validvariable += 1
                            continue

                        elif(inputsplit[1] == "I"):
                            if(loggedin == False):
                                sys.stdout.write("530 Not logged in.\r\n")
                                c.send("530 Not logged in.\r\n".encode())
                                continue

                            if(validcommands[validvariable] == "USER" or validcommands[validvariable] == "PORT"):
                                sys.stdout.write("503 Bad sequence of commands.\r\n")
                                c.send("503 Bad sequence of commands.\r\n".encode())
                                continue

                            sys.stdout.write("200 Type set to I.\r\n")
                            validcommands.append("TYPEI")
                            c.send("200 Type set to I.\r\n".encode())
                            validvariable += 1
                            continue

                        else:
                            sys.stdout.write("501 Syntax error in parameter.\r\n")
                            c.send("501 Syntax error in parameter.\r\n".encode())

                    if(firstupperinput == "PORT" or firstupperinput == "RETR"):
                        if(loggedin == False):
                            sys.stdout.write("530 Not logged in.\r\n")
                            c.send("530 Not logged in.\r\n".encode())
                            continue

                        if(firstupperinput == "PORT"):
                            portinput = inputsplit[1].lstrip()
                            portsplit = portinput.split(",", 5)[0:6]
                            portsplitlength = len(portsplit)

                            if(portsplitlength != 6):
                                sys.stdout.write("501 Syntax error in parameter.\r\n")
                                c.send("501 Syntax error in parameter.\r\n".encode())
                                continue
                            else:
                                #loop through port parameter to check if given input is integer between 0 and 255
                                portparamatervalid = True
                                for a in portsplit:
                                    if(a.isdigit() == True):
                                        if(int(a) >= 0 and int(a) <= 255):
                                            continue
                                        else:
                                            portparamatervalid = False
                                            break
                                    else:
                                        portparamatervalid = False
                                        break

                                if(portparamatervalid == False):
                                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                                    c.send("501 Syntax error in parameter.\r\n".encode())
                                    continue

                                validcommands.append("PORT")
                                validvariable += 1

                                ipaddress = portsplit[0]+"."+portsplit[1]+"."+portsplit[2]+"."+portsplit[3]
                                portnumber = (int(portsplit[4])*256) + int(portsplit[5])
                                sys.stdout.write("200 Port command successful ("+ipaddress+","+str(portnumber)+").\r\n")
                                portsuccess = "200 Port command successful ("+ipaddress+","+str(portnumber)+").\r\n"
                                c.send(portsuccess.encode())
                                continue

                        else:
                            if(validcommands[validvariable] == "PORT"):
                                strlist = list(inputsplit[1])
                                isvalid = 0

                                retrcommand = inputsplit[1].lstrip(' /\\')

                                #check if retr command is valid, also using a for loop
                                if('\r' in retrcommand or '\n' in retrcommand):
                                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                                    c.send("501 Syntax error in parameter.\r\n".encode())
                                    continue

                                for i in strlist:
                                    asciivalue = ord(i)
                                    if(asciivalue > 127):
                                        isvalid += 1
                                    else:
                                        isvalid += 0

                                if(isvalid > 0):
                                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                                    c.send("501 Syntax error in parameter.\r\n".encode())
                                    continue

                                filesplit = retrcommand.split("/")

                                #check if retr_files folder exists, if it doesn't then create it
                                if(os.path.exists(os.path.join(os.getcwd(), "retr_files")) == False):
                                    os.mkdir(os.path.join(os.getcwd(), "retr_files"))

                                #check if given file exists, if it does then copy it while giving appropriate ftp replies and naming new file correct
                                path = os.path.join(os.getcwd(), retrcommand)
                                if os.path.isfile(path):
                                    sys.stdout.write("150 File status okay.\r\n")
                                    c.send("150 File status okay.\r\n".encode())

                                    try:
                                        sendtoclientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        sendtoclientsocket.connect((ipaddress, int(portnumber)))
                                    except socket.error as err:
                                        c.send("425 Can not open data connection.\r\n".encode())
                                        continue

                                    try:
                                        file = open(path,"rb")
                                        minifile = file.read()
                                        sendtoclientsocket.send(minifile)

                                        file.close()
                                        sendtoclientsocket.close()

                                        sys.stdout.write("250 Requested file action completed.\r\n")
                                        c.send("250 Requested file action completed.\r\n".encode())

                                        validcommands.append("RETR")
                                        validvariable += 1

                                        continue
                                    except:
                                        sys.stdout.write("550 File not found or access denied.\r\n")
                                        c.send("550 File not found or access denied.\r\n".encode())
                                        continue

                                else:
                                    sys.stdout.write("550 File not found or access denied.\r\n")
                                    c.send("550 File not found or access denied.\r\n".encode())
                                    continue

                            else:
                                sys.stdout.write("503 Bad sequence of commands.\r\n")
                                c.send("503 Bad sequence of commands.\r\n".encode())

                else:
                    sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                    c.send("500 Syntax error, command unrecognized.\r\n".encode())

            #edge cases where \r\n may be missing either \r or \n or all 3
            elif '\r' in line:
                #edge case with \r i.e \r\r\r\r
                howmanycrs = userinput[x].count('\r')
                splitnewline = userinput[x].split("\r", howmanycrs)[0:2]
                print(splitnewline[0], end="\r\n")
                sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                c.send("500 Syntax error, command unrecognized.\r\n".encode())


            elif '\n' in line:
                #edge case with \n i.e \n\n\n\n
                howmanylfs = userinput[x].count('\n')
                splitnewline = userinput[x].split("\n", howmanylfs)[0:2]
                print(splitnewline[0], end="\n")
                sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                c.send("500 Syntax error, command unrecognized.\r\n".encode())

            else:
                print(line)
                sys.stdout.write("500 Syntax error, command unrecognized.\r\n")
                c.send("500 Syntax error, command unrecognized.\r\n".encode())

        if(gotquit == True):
            break
