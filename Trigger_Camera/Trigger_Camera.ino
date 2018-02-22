/*send the trigger for testing the camera
 * Created by Chang Liu
 * 2018-Jan-26
 */
 
const int triggerPin = 2; //trigger pin option

void setup() {
  // initialize the digital pin LED_BUILTIN as an output
  // initialize the digital pin D2 as the trigger output
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(triggerPin, OUTPUT);

}

void loop() {
  
  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(triggerPin, HIGH);
  delay(8);

  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(triggerPin, LOW);
  delay(8); 

  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(triggerPin, HIGH);
  delay(8);

  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(triggerPin, LOW);
  delay(8);  

  digitalWrite(LED_BUILTIN, HIGH); 
  digitalWrite(triggerPin, HIGH);
  delay(8);

  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(triggerPin, LOW);
  delay(8);  

  delay(2000); 

}
