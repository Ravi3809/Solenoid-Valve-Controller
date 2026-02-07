const int VALVE_PIN = 8; // Connect to the 2k Ohm base resistor
const int TRIG_PIN=2;
int TRIGGER=0;
void setup() {
  pinMode(VALVE_PIN, OUTPUT);
  pinMode(TRIG_PIN, INPUT);
  digitalWrite(VALVE_PIN, LOW); // Starts with valve CLOSED
  Serial.begin(9600);  //Setting baud rate 9600
  Serial.println("Solenoid Valve Control");
  Serial.println("Logic: Normally Closed (HIGH = Flow, LOW = Stop)");
  Serial.println("--- 12V Solenoid Control System Ready ---");
  Serial.println("System starting in 2 seconds...");
  delay(2000);
}

void loop() {
  //Step 1: Check the trigger 
  TRIGGER = digitalRead(TRIG_PIN);

  // Check if the Tigger is High.
  if (TRIGGER == HIGH) {
    // Turn Valve ON
    Serial.println("Valve ON");
    digitalWrite(VALVE_PIN, HIGH);
  } else {
    // Turn Valve OFF
    Serial.println("Valve OFF");
    digitalWrite(VALVE_PIN, LOW);
  }
}
