/* Testing the IR Range finder */

int irPin = A4;
int irVal = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  irVal = analogRead(irPin);
  Serial.println(irVal);
  delay(50);
}

