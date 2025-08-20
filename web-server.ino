

#include "WiFiS3.h"

#include "arduino_secrets.h" 
char ssid[] = SECRET_SSID;        
char pass[] = SECRET_PASS;   
int keyIndex = 0;                

int red = 7;
int green = 8;

int trig = 2;
int echo = 3;
long duration;
float distance;

  /* ******************************************** */
  //TODO: 
  //REPLACE LEDS WITH MOTOR CONTROL PINS
  //DURING CONTINUED RESEARCH + PUBLICATION WORK THROUGHOUT SEPTEMBER '25
  //REPLACE DISTANCE SENSING FILLER DATA WITH MOISTURE + NPK SENSING FROM SEPARATE NPK ARDUINO UNO R3
  //Due to components and sensors arriving late, I was invited back to continue this project through September and October 2025 with the goal of getting an IEEE publication.
  //Code is written and prepared for all the sensors, however, they are not field ready, hence the use of the distance sensor 
  //and LEDs rather than the requisite sensors.
  //Code prepared for the moisture, NPK, temperature, humidity, and co2 sensors can be found in soilhealth.ino, 
  //and will be integrated into the webserver in a future commit.
  /* ******************************************** */
int status = WL_IDLE_STATUS;
WiFiServer server(80);

void setup() {
  Serial.begin(9600);      // initialize serial communication
  pinMode(red, OUTPUT);      // set the LED pin mode
  pinMode(green, OUTPUT);      // set the LED pin mode
    
  pinMode(trig, OUTPUT); // Trig is output
  pinMode(echo, INPUT);  // Echo is input

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
  Serial.print("Attempting to connect to SSID: ");
  Serial.println(ssid);
  Serial.println(pass);


  status = WiFi.begin(ssid, pass);
  
  Serial.print("WiFi status code: ");
  Serial.println(status);
  
  // Wait and check intermediate status
  for(int i = 0; i < 10; i++) {
    delay(1000);
    status = WiFi.status();
    Serial.print("Status after ");
    Serial.print(i+1);
    Serial.print(" seconds: ");
    Serial.println(status);
    if(status == WL_CONNECTED) break;
  }
  
  if(status != WL_CONNECTED) {
    Serial.println("Failed to connect, retrying...");
  }
}
  server.begin();                           // start the web server on port 80
  printWifiStatus();                        // you're connected now, so print out the status
}


void loop() {
  WiFiClient client = server.available();   // listen for incoming clients
  
  if (client) {                             // if you get a client,
    Serial.println("new client");           // print a message out the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    bool json_response_sent = false;
    while (client.connected()) {            // loop while the client's connected
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        Serial.write(c);                    // print it out to the serial monitor
      

        if (c == '\n') {                    // if the byte is a newline character

          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0 && json_response_sent == false) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println();

            // the content of the HTTP response follows the header:
            // client.print("<p style=\"font-size:7vw;\">Click <a href=\"/ON8\">here</a> extend motor<br></p>");
            // client.print("<p style=\"font-size:7vw;\">Click <a href=\"/OFF8\">here</a> retract motor <br></p>");
            // client.print("<p style=\"font-size:7vw;\">Click <a href=\"/stop\">here</a> brake motor<br></p>");
            // client.print("<p style=\"font-size:7vw;\">Click <a href=\"/gather_data\">here</a> gather data<br></p>");
            // The HTTP response ends with another blank line:
            client.println();
            // break out of the while loop:
            client.stop(); //disconnect
            break;
          } else {    // if you got a newline, then clear currentLine:
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
        // Check to see if the client request was "GET ...
        if (currentLine.endsWith("GET /ON8")) {

          Serial.println(currentLine);
          Serial.println("green");
          digitalWrite(green, HIGH);               // GET /H turns the Green LED on
          digitalWrite(red, LOW);               // GET /H turns the Red LED off
        }
        if (currentLine.endsWith("GET /OFF8")) {
          Serial.println(currentLine);
          Serial.println("red");
          digitalWrite(green, LOW);               
          digitalWrite(red, HIGH);             
        }
        if (currentLine.endsWith("GET /stop")) {
          Serial.println(currentLine);
          Serial.println("braked");
          digitalWrite(green, LOW);             
          digitalWrite(red, LOW);               
        }

        if (currentLine.endsWith("GET /gather_data")) {
          Serial.println(currentLine);
          //get start time
          unsigned long startTime = millis();
          //if current time - when we started is less than 90s
          int runDuration = 90000;

          //create string array of sensor data
          float distance_sensor_data[200];
          String json = "{";
          /* ******************************************** */
          //TODO: DURING CONTINUED RESEARCH + PUBLICATION WORK THROUGHOUT SEPTEMBER '25
          //REPLACE DISTANCE SENSING FILLER DATA WITH MOISTURE + NPK SENSING FROM SEPARATE NPK ARDUINO UNO R3
          /* ******************************************** */
          int distance_sensor_data_index = 0;
          while (millis() - startTime < runDuration) {
              digitalWrite(trig, LOW);
              delayMicroseconds(2);

              // Send a 10 microsecond pulse to trigger the sensor
              digitalWrite(trig, HIGH);
              delayMicroseconds(10);
              digitalWrite(trig, LOW);

              // Read the pulse duration on Echo
              duration = pulseIn(echo, HIGH);

              // Calculate distance in cm
              distance = (duration * 0.0343) / 2; // 0.0343 cm per microsecond, divide by 2 for round trip

              // Print the distance
              Serial.print("Distance: ");
              Serial.print(distance);
              Serial.println(" cm");
              delay(1000);
              //set value in array to distance
              distance_sensor_data[distance_sensor_data_index] = distance;
              //increment index
              distance_sensor_data_index++;
          }
          //loop through sensor data index
          //create json property known as distance
          json = json + " \"distance\":  [";
          for (int i = 0; i < distance_sensor_data_index; i++) {
            json = json + String(distance_sensor_data[i]); //append sensor data to json
            if (i < distance_sensor_data_index - 1) {
              json += ", "; //if before the last one, add a comma
            } else {
              json = json + "]}"; //if it is the last one, close it
            }
          }
          Serial.println(json);

          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: application/json");
          client.println("Connection: close");
          client.println();
          client.println(json);
          json_response_sent = true;
          delay(1);
          break; //break out of loop
        }
      }
      
    }
    // close the connection:
    client.stop();
    json_response_sent = false;
    Serial.println("client disconnected");
  }
}

void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
  Serial.print("Gateway: ");
  Serial.println(WiFi.gatewayIP());

  // print where to go in a browser:
  Serial.print("To see this page in action, open a browser to http://");
  Serial.println(ip);
}
