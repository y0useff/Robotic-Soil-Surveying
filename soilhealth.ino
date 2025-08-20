#include <DHT.h>

/************************Hardware Related Macros************************************/
///CO2 Sensor
#define         MG_PIN                       (A0)     //define which analog input channel you are going to use
#define         BOOL_PIN                     (2)
#define         DC_GAIN                      (8.5)   //define the DC gain of amplifier
//DHT 11 temp humid
#define         DHTPIN                         2       // Define the pin used to connect the sensor
//HW-101 Capacitive Moisture Sensoring 
#define moisturePin A5



/***********************Software Related Macros************************************/
//CO2 Sensor
#define         READ_SAMPLE_INTERVAL         (50)    //define how many samples you are going to take in normal operation
#define         READ_SAMPLE_TIMES            (5)     //define the time interval(in milisecond) between each samples in
                                                     //normal operation

/**********************Application Related Macros**********************************/
//These two values differ from sensor to sensor. user should derermine this value.
#define         ZERO_POINT_VOLTAGE           (0.388) //define the output of the sensor in volts when the concentration of CO2 is 400PPM
#define         REACTION_VOLTGAE             (0.030) //define the voltage drop of the sensor when move the sensor from air into 1000ppm CO2

//DHT 11 temp humid
#define DHTTYPE DHT11  // Define the sensor type
//Create object for dht-11
DHT dht(DHTPIN, DHTTYPE);  // Create a DHT object



/*****************************Globals***********************************************/
float           CO2Curve[3]  =  {2.602,ZERO_POINT_VOLTAGE,(REACTION_VOLTGAE/(2.602-3))};
                                                     //two points are taken from the curve.
                                                     //with these two points, a line is formed which is
                                                     //"approximately equivalent" to the original curve.
                                                     //data format:{ x, y, slope}; point1: (lg400, 0.324), point2: (lg4000, 0.280)
                                                     //slope = ( reaction voltage ) / (log400 –log1000)

String getCO2PPM() {
    int percentage;
    float volts;

    volts = MGRead(MG_PIN);
    Serial.print( "MG811 CO2:" );
    Serial.print(volts);
    Serial.print( "V           " );
    String output_co2 = "";
    percentage = MGGetPercentage(volts,CO2Curve);
    Serial.print("CO2:");
    // Serial.print(percentage);
    if (percentage == -1) {
        output_co2 = "Below 410 PPM\n";
    } else {
        output_co2 = String(percentage) + " ppm\n";
    }

    // Serial.print( "ppm" );
    // Serial.print("\n");

    //uncomment if need to debug or check voltage
    // if (digitalRead(BOOL_PIN) ){
    //     Serial.print( "=====BOOL is HIGH======" );
    // } else {
    //     Serial.print( "=====BOOL is LOW======" );
    // }
    delay(500);
    return output_co2;
}

float getAbsoluteMoisture(int sensorValue) {
  const int dryValue = 490;
  const int wetValue = 190;

  // clamp the sensorValue to stay within the calibration range
  if (sensorValue > dryValue) sensorValue = dryValue;
  if (sensorValue < wetValue) sensorValue = wetValue;

  // map to percentage: higher moisture means higher percentage
  float moisturePercent = 100.0 * (dryValue - sensorValue) / (dryValue - wetValue);
  return moisturePercent;
}

void printTempHumid() {
  delay(2000);

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  // float f = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  // Compute heat index in Fahrenheit (the default)
  // float hif = dht.computeHeatIndex(f, h);
  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(t, h, false);

  // Print the humidity, temperature, and heat index values to the serial monitor
  Serial.print(F("Humidity: "));
  Serial.print(h);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);
  Serial.println(F("°C "));
}

void setup() {
  // put your setup code here, to run once:
    Serial.begin(9600);                              //UART setup, baudrate = 9600bps
    //open up serial monitor
    //CO2 Pin Setup
    pinMode(BOOL_PIN, INPUT);                        //set pin to input
    digitalWrite(BOOL_PIN, HIGH);   
    //dht-11 sensor initialization
    dht.begin();  // Initialize the DHT sensor
   
}

void loop() {
  Serial.println(getCO2PPM());
  Serial.println(String(getAbsoluteMoisture(analogRead(moisturePin))) + "% Moisture");
  printTempHumid();
}



//other functions for co2 reading
float MGRead(int mg_pin)
{
    int i;
    float v=0;

    for (i=0;i<READ_SAMPLE_TIMES;i++) {
        v += analogRead(mg_pin);
        delay(READ_SAMPLE_INTERVAL);
    }
    v = (v/READ_SAMPLE_TIMES) *5/1024 ;
    return v;
}

/*****************************  MQGetPercentage **********************************
Input:   volts   - SEN-000007 output measured in volts
         pcurve  - pointer to the curve of the target gas
Output:  ppm of the target gas
Remarks: By using the slope and a point of the line. The x(logarithmic value of ppm)
         of the line could be derived if y(MG-811 output) is provided. As it is a
         logarithmic coordinate, power of 10 is used to convert the result to non-logarithmic
         value.
************************************************************************************/
int  MGGetPercentage(float volts, float *pcurve)
{
   if ((volts/DC_GAIN )>=ZERO_POINT_VOLTAGE) {
      return -1;
   } else {
      return pow(10, ((volts/DC_GAIN)-pcurve[1])/pcurve[2]+pcurve[0]);
   }
}
