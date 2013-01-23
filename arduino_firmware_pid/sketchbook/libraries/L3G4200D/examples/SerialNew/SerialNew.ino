#include <Wire.h>
#include <L3G4200D.h>
#include <ADXL345.h>

L3G4200D gyro;
ADXL345 accel;

const float alpha = 0.5;

double fXg = 0;
double fYg = 0;
double fZg = 0;
double prevfXg = 0;
double prevfYg = 0;

double vX = 0;
double vY = 0;
double prevvX = 0;
double prevvY = 0;

double X = 0;
double Y = 0;

ADXL345 acc;

int time = millis();
double yawRate, prevYawRate = 0;
double yawAngle = 0;
int rotationThreshold = 100;

//double vX, vY;
//double prevfXg = 0, prevfYg = 0;
double calcAngle = 0;
int threshold = 1;   //z accelerometer threshold

void setup() {
  Serial.begin(9600);
  Wire.begin();

  gyro.enableDefault();
  accel.begin();
  
  delay(100);
}

void loop() {
  gyro.read();  
  if (millis()-time > 10){
    // integration every 10 ms
    time = millis();  //update time
    yawRate = (double)gyro.g.z / 4.0;
    if (yawRate >= rotationThreshold || yawRate <= -rotationThreshold)
      yawAngle += ((prevYawRate + yawRate)*10.0)/2000.0;
    else{
      Serial.println("ignored");
    }
    prevYawRate = yawRate;
    
    //yawAngle = (int) yawAngle % 360;
    //Serial.println((long) yawAngle);
    
    double pitch, roll, Xg, Yg, Zg;
    acc.read(&Xg, &Yg, &Zg);

    //Low Pass Filter
    fXg = Xg * alpha + (fXg * (1.0 - alpha));
    fYg = Yg * alpha + (fYg * (1.0 - alpha));
    fZg = Zg * alpha + (fZg * (1.0 - alpha));

    //Roll & Pitch Equations
    //roll  = (atan2(-fYg, fZg)*180.0)/M_PI;
    //pitch = (atan2(fXg, sqrt(fYg*fYg + fZg*fZg))*180.0)/M_PI;
    //yaw = (atan2(sqrt(fXg^2 + fZg^2),fZg)*180.0)/M_PI;

    //Serial.print(pitch);
    //Serial.print(":");
    //Serial.println(roll);
    
//    time = millis();  //update time
    if (abs(fXg) - 0.17 > 0.03 && abs(fYg)-0.07 > 0.03){
      vX += ((prevfXg + fXg)*10.0)/2000.0;
      vY += ((prevfYg + fYg)*10.0)/2000.0;
      X += ((prevvX + vX)*10.0)/2000.0;
      Y += ((prevvY + vY)*10.0)/2000.0;
    }
    else{
      Serial.println("ignored");
    }
    prevfXg = fXg;
    prevfYg = fYg;
    prevvX = vX;
    prevvY = vY;
    
    calcAngle += (atan2(X, Y)*180.0)/M_PI;
    
/*    Serial.println(fXg);
    Serial.println(fYg);
    if (abs(fXg) - 0.17 > 0.03 || abs(fYg)-0.07 > 0.03){      
      calcAngle += (atan2(sqrt(fXg*fXg + fZg*fZg),fYg)*180.0)/M_PI;
//      if calcA
      calcAngle = (int) calcAngle % 360;
//      Serial.println (calcAngle);   
    } 
//    prevfXg = fXg;
//    prevfYg = fYg;
*/
    if (yawAngle < 0)
      yawAngle += 360;
    else if (yawAngle > 359)
      {yawAngle -= 360;}

    if (calcAngle < 0)
      calcAngle += 360;
    else if (calcAngle > 359)
      {calcAngle -= 360;}
      
    Serial.print(yawAngle);
    Serial.print(":");
    Serial.println(calcAngle);    
//    delay(10);
  }

  delay(200); 
}
