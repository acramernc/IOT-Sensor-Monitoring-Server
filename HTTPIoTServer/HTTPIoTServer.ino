/*********
  Original for ESP8266 -- Rui Santos
  Complete project details at http://randomnerdtutorials.com  

  Modified for NodeMCU -- Luke Rumbaugh 03 March 19

  Reworked for access by socket client -- Luke Rumbaugh 14 November 19
*********/
#include <ESP8266WiFi.h> // Library for Wi-Fi connection
#include "DHT.h"          // Library for DHT sensor

int PIN_DIGITAL_SENSOR = D3;
int PIN_ANALOG_SENSOR = D2;
int PIN_LED_BUILTIN = D0;
int PIN_LED_OUT = D1;

// Replace with your network credentials
const char* ssid     = "GCC";
const char* password = "";

// Set web server port number to 80
WiFiServer server(80);

// Initialize DHT sensor
DHT dht(PIN_ANALOG_SENSOR, DHT11);

// State variables
bool ledState = LOW;

String outputIntState = "off";
String outputExtState = "off";
String inputExtState = "LOW";

// SETUP FUNCTION
void setup() {

  // Task 1: Initialize the serial link to the PC
  Serial.begin(115200);
  delay(1000);
  
  // Task 2: Configure pins as inputs & outputs, and set outputs to default values
  pinMode(PIN_DIGITAL_SENSOR, INPUT);
  pinMode(PIN_ANALOG_SENSOR, INPUT);
  pinMode(PIN_LED_BUILTIN, OUTPUT);
  pinMode(PIN_LED_OUT, OUTPUT);
  digitalWrite(PIN_LED_OUT, LOW);
  ledState = LOW;

  // Task 3: Start the analog DHT sensor
  dht.begin();

  // Task 4: Print the MAC address 
  Serial.println();
  Serial.print("Device with MAC address "); Serial.print(WiFi.macAddress()); Serial.println(" reporting for duty.");
  delay(1000);
  
  // Task 5: Connect to network
  //  attempt
  Serial.print("Connecting to "); Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("...attempting to connect to SSID ");
    Serial.print(ssid);
    Serial.println("...");
  }
  //  confirm
  Serial.println("it worked!");
  Serial.print("WiFi connected to SSID ");
  Serial.println(ssid);

  // Task 6: Print the IP address obtained
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // Task 7: Start web server
  server.begin(); // on port 80
}

// LOOP FUNCTION
void loop(){

  // Variable to store the HTTP request
  String header;
  // Task 1: Listen for client
  WiFiClient client = server.available();   // Listen for incoming clients
  Serial.println("Waiting for client connection.");
  
  // Task 2: Connect to client and read message from client
  if (client) {                             // If a new client connects,
    Serial.println("Client connection established");          // print a message out in the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    while (client.connected()) {            // loop while the client's connected
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        Serial.write(c);                    // print it out the serial monitor
        header += c;

        // End of HTTP message
        if (c == '\n') {                    // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();

            // Message Handler 1: Toggle LED
            if (header.indexOf("GET /toggleLED") >=0) {
              ledState = !ledState; // toggle state
              digitalWrite(PIN_LED_OUT, ledState); 
              Serial.print("Toggling LED to "); Serial.println(ledState);
              client.print("Toggling LED to "); client.println(ledState); client.println();
            }
            
            // Message Handler 2: Get analog sensor value 
            else if (header.indexOf("GET /getAnalog") >=0) {
              int N = 10;                   // number of readings to average
              float tempValueSum = 0;       // temporary variable for sum of averages
              for (int ii=0;ii<N;ii++){        // take N readings and average them
                tempValueSum = tempValueSum + dht.readTemperature(true);  // take each reading
              }
              float tempValue = tempValueSum / N;     // average readings
              //float tempValue = dht.readTemperature(true); // read 
              Serial.print("Temperature value is "); Serial.print(tempValue); Serial.println(" deg F, which will be passed to remote client.");
              client.print("Temperature value is "); client.print(tempValue); client.println(" deg F"); client.println();
            }
            
            // Message Handler 3: Get digital sensor value
            else if (header.indexOf("GET /getDigital") >=0) {
              int sensorValue = !digitalRead(PIN_DIGITAL_SENSOR); // read 
              Serial.print("Digital sensor value is "); Serial.print(sensorValue); Serial.println(", which will be passed to remote client."); 
              client.print("Digital sensor value is "); client.println(sensorValue); client.println();
            }
            
            // Message Handler 4: Quit
            else if (header.indexOf("GET /quit") >0 ) {
              Serial.println("Disconnecting at client request."); 
              client.println("Disconnecting."); client.println();
              client.stop();
            }
            
            // Break out of the while loop
            break;
            
          } else { // if you got a newline, then clear currentLine
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
  }

  // Task 2: Flash the built-in LED 
  delay(500);
  digitalWrite(PIN_LED_BUILTIN,1);
  delay(500);
  digitalWrite(PIN_LED_BUILTIN,0);
  
}
