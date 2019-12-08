#Jake Murphy and Adam Cramer
import socket, smtplib, threading, os, time

HOST = input("Enter hostname of server: ")
PORT = 80
password = "pass123"

def connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connection Successful!")
        while True:
            print("1. List hardware")
            print("2. Query specific sensor value")
            print("3. Query all sensor values")
            print("4. Set actuator value")
            print("5. Set alarm condition")
            print("6. Start logging sensor data")
            print("7. Stop logging sensor data")
            print("8. Quit")
            cmd = input("What would you like to do (1-8)?: ")
            if int(cmd) == 1:
                print("Proximity Sensor : D4 \n DHT : D2 \n External LED : D1 \n Alert LED : D5")
                break
            elif int(cmd) == 2:
                #Query Sensor
                sensor = input("Which sensor would you like to query?: ")
                request = 'GET /sensors/' + sensor + ' HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                s.send(b'' + request.encode())
                result = s.recv(1024)
                print(result)
            elif int(cmd) == 3:
                #Query all sensor values
                request = 'GET /sensors/ HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                s.send(b'')
                result = s.recv(1024)
                print(result)
            elif int(cmd) == 4:
                #Set actuator value
                actuator = input("Enter 1 for LED or 2 for Buzzer: ")
                actuatorValue = input("Enter value of actuator: ")
                passwordGuess = input("Please enter password to complete: ")
                if password == passwordGuess:
                    if actuator == "1":
                        request = 'PUT /led/' + actuatorValue + ' HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                    else:
                        request = 'PUT /buzz/' + actuatorValue + ' HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                    s.send(b'' + request.encode())
                    result = s.recv(1024)
                    print(result)
                else:
                    print("Wrong password!!")
            elif int(cmd) == 5:
                #Set alarm condition
                sensorValue = input("Which sensor would you like to query?: ")
                request = 'GET /sensors/' + sensorValue + ' HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                s.send(b'' + request.encode())
                result = s.recv(1024)
                print(result)
                t2 = threading.Thread(target=alarm, args=(sensorValue,))
                t2.start()
            elif int(cmd) == 6:
                #Start logging sensor data
                sensorValue = input("Which sensor would you like to query?: ")
                request = 'GET /sensors/' + sensorValue + ' HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                s.send(b'' + request.encode())
                result = s.recv(1024)
                print(result)
            elif int(cmd) == 7:
                #Stop logging sensor data
                sensorValue = input("Which sensor would you like to query?: ")
                request = 'GET /sensors/' + sensorValue + ' HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
                s.send(b'' + request.encode())
                result = s.recv(1024)
                print(result)
            else:
                #Quit
                print("Terminating Program...")
                os._exit(0)

def alarm(sensorValue):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            time.sleep(15)
            request = 'GET /sensors/' + sensorValue + ' HTTP/1.1\r\nHost: ' + HOST + '\r\n\r\n'
            s.send(b'' + request.encode())
            result = s.recv(1024)
            print(result)
            #Send email or text when alarm triggered?
            #mailer = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            #gmail_user = 'comp342gccf19@gmail.com'
            #gmail_password = 'P@$$word1!'
            #mailer.login(gmail_user, gmail_password)
            #msg1= "From: Jake Murphy \r\nTo: Dr. Rumbaugh \r\nSubject: Lab 3 \r\nThe value of the square root of 17 is " + (str)(root) +"\r\n"
            #mailer.sendmail(gmail_user, gmail_user, msg1)

if __name__== "__main__":

    t1 = threading.Thread(target=connect)
    t1.start()

    t1.join()
    #t2.join()

