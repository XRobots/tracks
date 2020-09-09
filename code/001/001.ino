#include <Servo.h>

Servo servo1; 
Servo servo2; 

unsigned long start1;
int pwm1;
unsigned long start2;
int pwm2;

int output1;
int output2;

void setup() {

    pinMode(2, INPUT);    // input from r/c rec
    pinMode(3, INPUT);    // input from r/c rec
    attachInterrupt(0, timeit1, CHANGE);     // pin 2
    attachInterrupt(1, timeit2, CHANGE);     // pin 3

    servo1.attach(4);
    servo2.attach(5);
    
}

void loop() {

    output1 = pwm1 + (pwm2-1500);
    output2 = pwm1 - (pwm2-1500);

    output1 = constrain(output1,1300,1700);
    output2 = constrain(output2,1300,1700);

    servo1.writeMicroseconds(output1);
    servo2.writeMicroseconds(output2);        
    
}


// timer functions

void timeit1() {
    if (digitalRead(2) == HIGH) {
      start1 = micros();
    }
    else {
      pwm1 = micros() - start1;
    }
  }


void timeit2() {
    if (digitalRead(3) == HIGH) {
      start2 = micros();
    }
    else {
      pwm2 = micros() - start2;
    }
  }
