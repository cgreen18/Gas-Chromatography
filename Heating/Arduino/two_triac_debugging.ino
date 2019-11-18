/*  Title: two_triac_debugging.ino
 *  Author: Conor Green and Matt McPartlan
 *  Description: Script to work with two triacs
 *  Usage: Upload to microcontroller with interrupt capability. Arduino Pro Micro 5V used.
 *  Version:
 *    1.0 - November 17 2019 - First creation. Taken from three_element_heat_control
 */

// Oven pins
int inter_oven = 2;
int triac_oven = 4;

// Oven variables (defaults)
unsigned int dim_oven = 1024;


// Injector and detector pins
int triac_inj_det = 5;

// Injector and detector variables
unsigned int dim_inj_det = 1024;


void setup() {
  Serial.begin(9600);
  
  pinMode(triac_inj_det,OUTPUT);
  pinMode(triac_oven,OUTPUT);
  attachInterrupt(digitalPinToInterrupt(inter_oven), zc_interrupt, RISING);

}

void zc_interrupt(){
  digitalWrite(triac_inj_det,LOW);  
  digitalWrite(triac_oven,LOW);
  
  
    
  delayMicroseconds(2000);
  digitalWrite(triac_inj_det,HIGH);
  delayMicroseconds(8.33);
  digitalWrite(triac_inj_det,LOW);
  delayMicroseconds(1000);
  digitalWrite(triac_oven,HIGH);
  delayMicroseconds(8.33);
  digitalWrite(triac_oven,LOW);

  
}

void update_dimming(){
  dim_oven = 2000;
  dim_inj_det = 3000;
  
}


void loop() {
  update_dimming();
  Serial.println("loop");
  
}
