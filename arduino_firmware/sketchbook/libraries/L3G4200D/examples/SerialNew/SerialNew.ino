#include <Wire.h>
#include <L3G4200D.h>

L3G4200D gyro;

int time = millis();
long yawRate, prevYawRate = 0;
long yawAngle = 0;
int rotationThreshold = 100;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  gyro.enableDefault();
  
}

void loop() {
  gyro.read();

  Serial.print("G ");
  Serial.print("X: ");
  Serial.print((int)gyro.g.x);
  Serial.print(" Y: ");
  Serial.print((int)gyro.g.y);
  Serial.print(" Z: ");
  Serial.println((int)gyro.g.z);
  
  if (millis()-time > 5){
    // integration every 10 ms
    time = millis();  //update time
    yawRate = (long)gyro.g.z / 4;
    if (yawRate >= rotationThreshold || yawRate <= -rotationThreshold)
      yawAngle += ((long)(prevYawRate + yawRate)*10)/2000;
    else
      Serial.println("ignored");
    prevYawRate = yawRate;
    
    if (yawAngle < 0)
      yawAngle += 360;
    else if (yawAngle > 359)
      yawAngle -= 360;
    Serial.println((long) yawAngle);
  }

  delay(300);
  
  
}
