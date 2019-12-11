#Jake Murphy and Adam Cramer
import socket, smtplib, threading, os, time

HOST = input("Enter hostname of server: ")
PORT = 80
password = "pass123"
auth = False
lock = threading.Lock()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#values for multithreading
fStop = True
eStop = True
tLog = False
hLog = False
pLog = False



def connect():
    global fStop
    global eStop
    global tLog
    global hLog
    global pLog
    global auth #has the user entered the password yet
    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connection Successful!")
    while True:
        lock.acquire()
        print("1. List hardware")
        print("2. Query specific sensor value")
        print("3. Query all sensor values")
        print("4. Set actuator value")
        print("5. Set alarm condition")
        print("6. Start logging sensor data")
        print("7. Stop logging sensor data")
        print("8. Quit")
        lock.release()
        cmd = input("What would you like to do (1-8)?: ")

        if int(cmd) == 1:
            lock.acquire()
            print("Proximity Sensor : D4 \n DHT : D2 \n External LED : D1 \n Alert LED : D5")
            lock.release()
        elif int(cmd) == 2:
            #Query Sensor
            lock.acquire()
            sensor = input("Which sensor would you like to query?: ")
            request = 'GET /sensors/' + sensor + ' HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
            s.send(b'' + request.encode())
            time.sleep(0.1)
            result = s.recv(1024).decode()
            #print(result)
            result = result.split("close\r\n") #splits HTTP response right before text
            #print(result) #debugging
            if len(result) > 1:
                print(result[1])
            lock.release()
            result = ""
        elif int(cmd) == 3:
            #Query all sensor values
            lock.acquire()
            request = 'GET /sensors/ HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
            s.send(b'' + request.encode())
            time.sleep(0.1)
            result = s.recv(1024).decode()
            result = result.split("close\r\n")  # splits HTTP response right before text
            if len(result) > 1:
                print(result[1])
            lock.release()
        elif int(cmd) == 4:
            #Set actuator value

            actuator = input("Enter 1 for Outdoor LED or 2 for Alert LED: ")
            actuatorValue = input("Enter value of actuator: ")
            if not auth:
                passwordGuess = input("Please enter password to complete: ")
            if auth or password == passwordGuess:
                auth = True
                if actuator == "1":
                    request = 'PUT /led/' + actuatorValue + ' HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                else:
                    request = 'PUT /alert/' + actuatorValue + ' HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                lock.acquire()
                s.send(b'' + request.encode())
                time.sleep(0.1)
                result = s.recv(1024).decode()
                lock.release()
                if "OK" in result:
                    print("Success")
                else:
                    print("Error: Critical Failure")
            else:
                print("Wrong password!!")
        elif int(cmd) == 5:
            #Set alarm condition
            lock.acquire()
            print("1. Fire Alarm")
            print("2. Entryway Alarm")
            alarmValue = input("Which alarm would you like to arm?: ")
            lock.release()
            if int(alarmValue) == 1:
                if fStop:
                    lock.acquire()
                    request = 'GET /sensors/temperature HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                    s.send(b'' + request.encode())
                    time.sleep(0.1)
                    result = s.recv(1024).decode()
                    lock.release()
                    result = result.split("close\r\n")  # splits HTTP response right before text
                    if len(result) > 1:
                        print(result[1])

                    fStop = False
                else:
                    print("That alarm is already armed")
            elif int(alarmValue) == 2:
                if eStop:
                    lock.acquire()
                    request = 'GET /sensors/proximity HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                    s.send(b'' + request.encode())
                    time.sleep(0.1)
                    result = s.recv(1024).decode()
                    lock.release()
                    result = result.split("close\r\n")  # splits HTTP response right before text
                    print(result[1])

                    eStop = False
                else:
                    print("That alarm is already armed")
            else:
                print("Invalid alarm number")
        elif int(cmd) == 6:
            print("1. Temperature")
            print("2. Humidity")
            print("3. Proximity")
            print("4. All")
            sensor = input("Which sensor would you like to initiate logging on: ")
            sensor = int(sensor)

            if sensor == 1:
                tLog = True
                print("Temperature Logging Has Started")
            elif sensor == 2:
                hLog = True
                print("Humidity Logging Has Started")
            elif sensor == 3:
                pLog = True
                print("Proximity Logging Has Started")
            elif sensor == 4:
                tLog = hLog = pLog = True
                print("Complete Logging Has Started")
        elif int(cmd) == 7:
            print("1. Temperature")
            print("2. Humidity")
            print("3. Proximity")
            print("4. All")
            sensor = input("Which sensor would you like to stop logging on: ")
            sensor = int(sensor)

            if sensor == 1:
                tLog = False
                print("Temperature Logging Has Stopped")
            elif sensor == 2:
                hLog = False
                print("Humidity Logging Has Stopped")
            elif sensor == 3:
                pLog = False
                print("Proximity Logging Has Stopped")
            elif sensor == 4:
                tLog = hLog = pLog = False
                print("Logging Has Stopped")
        else:
            #Quit
            print("Terminating Program...")
            os._exit(0)

def alarm(subject, message):
    #Send email when alarm triggered
    mailer = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    mailer.ehlo()
    gmail_user = 'comp342gccf19@gmail.com'
    gmail_password = 'P@$$word1!'
    mailer.login(gmail_user, gmail_password)
    msg1= "From: Automated Security Systems \r\nTo: Homeowner \r\nSubject: "+ subject +"\r\n"+ message +"\r\n"
    mailer.sendmail(gmail_user, "acramernc@gmail.com", msg1) #from, to, message

def fire():
    global fStop
    while True:
        if not fStop:
            lock.acquire()
            request = 'GET /sensors/temperature HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
            s.send(b'' + request.encode())
            result = s.recv(1024).decode()
            lock.release()
            result = result.split("close\r\n")  # splits HTTP response right before text
            if len(result) > 1:
                #print(result)
                dataS = result[1].split(" ")
                #print(dataS)
                if len(dataS > 3):
                    data = float(dataS[3])
                else:
                    data = 0
            else:
                data = 0

            if data > 200:
                alarm("FIRE", "A fire has been detected in your home")
                fStop = True


def entry():
    global eStop
    while True:
        if not eStop:
            lock.acquire()
            request = 'GET /sensors/proximity HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
            s.send(b'' + request.encode())
            result = s.recv(1024).decode()
            lock.release()
            result = result.split("close\r\n")  # splits HTTP response right before text
            if len(result) >1:
                #print(result)
                dataS = result[1].split(" ")
                #print(dataS)
                if len(dataS) > 6:
                    data = dataS[6]
                else:
                    data = "NULL"
            else:
                data = "NULL"


            if "NOT" in data:
                alarm("Entryway Alarm", "Someone has opened the door")
                eStop = True

def log():
    global tLog
    global hLog
    global pLog
    while True:
        time.sleep(5)
        write = False
        msg = "" + time.ctime() + " "
        if tLog:
            lock.acquire()
            request = 'GET /sensors/temperature HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
            s.send(b'' + request.encode())
            time.sleep(0.1)
            result = s.recv(1024).decode()
            lock.release()
            result = result.split("close\r\n")  # splits HTTP response right before text
            if len(result) > 1:
                msg += result[1]
                write = True
        if hLog:
            lock.acquire()
            request = 'GET /sensors/humidity HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
            s.send(b'' + request.encode())
            time.sleep(0.1)
            result = s.recv(1024).decode()
            lock.release()
            result = result.split("close\r\n")  # splits HTTP response right before text
            if len(result) > 1:
                msg += result[1]
                write = True


        if pLog:
            lock.acquire()
            request = 'GET /sensors/proximity HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
            s.send(b'' + request.encode())
            result = s.recv(1024).decode()
            time.sleep(0.1)
            lock.release()
            result = result.split("close\r\n")  # splits HTTP response right before text
            if len(result) > 1:
                msg += result[1]
                write = True
        if write:
            f = open("log.txt", "a")
            f.write(msg + "\n")
            f.close()


fThread = threading.Thread(target=fire)
eThread = threading.Thread(target=entry)
lThread = threading.Thread(target=log)

fThread.start()
eThread.start()
lThread.start()
connect()

