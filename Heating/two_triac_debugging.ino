/*  Title: two_triac_debugging.ino
 *  Author: Conor Green and Matt McPartlan
 *  Description: Script to work with two triacs
 *  Usage: Upload to microcontroller with interrupt capability. Arduino Pro Micro 5V used.
 *  Version:
 *    1.0 - November 17 2019 - First creation. Taken from three_element_heat_control
 *    2.0 - November 17 2019 - Works as intended. Properly handles two triacs
 */

// Constants
int MAX_DELAY = 8140;
int MIN_DELAY = 425;

// Oven pins
int inter_oven = 2;
int triac_oven = 4;

// Oven variables (defaults)
unsigned int dim_oven = 2000;


// Injector and detector pins
int triac_inj_det = 5;

// Injector and detector variables
unsigned int dim_inj_det = 2000;


void setup() {
  Serial.begin(9600);
  
  pinMode(triac_inj_det,OUTPUT);
  pinMode(triac_oven,OUTPUT);
  attachInterrupt(digitalPinToInterrupt(inter_oven), zc_interrupt, RISING);

}

void zc_interrupt(){
  digitalWrite(triac_inj_det,LOW);  
  digitalWrite(triac_oven,LOW);

  float diff;


  //Case 1: delay -> 8.33 inj pulse -> diff delay -> 8.33 oven pulse
  if(dim_oven >= (dim_inj_det + 8.33)){
    diff = dim_oven - (dim_inj_det + 8.33);
    
    delayMicroseconds(dim_inj_det);
    digitalWrite(triac_inj_det,HIGH);
    delayMicroseconds(8.33);
    digitalWrite(triac_inj_det,LOW);
    delayMicroseconds(diff);
    digitalWrite(triac_oven,HIGH);
    delayMicroseconds(8.33);
    digitalWrite(triac_oven,LOW);
  }
  
  //Case 2: delay -> start inj pulse -> diff delay -> start oven pulse -> finish inj pulse -> finish oven pulse
  //Includes equal delay case
  else if(dim_oven >= dim_inj_det){
    diff = dim_oven - dim_inj_det;

    delayMicroseconds(dim_inj_det);
    digitalWrite(triac_inj_det,HIGH);
    delayMicroseconds(diff);
    digitalWrite(triac_oven,HIGH);
    delayMicroseconds(8.33-diff);
    digitalWrite(triac_inj_det,LOW);
    delayMicroseconds(diff);
    digitalWrite(triac_oven,LOW);
  }

  //Case 3: delay -> 8.33 oven pulse -> diff delay -> 8.33 inj pulse
  else if(dim_inj_det >= (dim_oven + 8.33)){
    diff = dim_inj_det - (dim_oven + 8.33);

    delayMicroseconds(dim_oven);
    digitalWrite(triac_oven,HIGH);
    delayMicroseconds(8.33);
    digitalWrite(triac_oven,LOW);
    delayMicroseconds(diff);    
    digitalWrite(triac_inj_det,HIGH);
    delayMicroseconds(8.33);
    digitalWrite(triac_inj_det,LOW);    
  }

  //Case 2: delay -> start oven pulse -> diff delay -> start inj pulse -> finish oven pulse -> finish inj pulse 
  else if(dim_inj_det >= dim_oven){
    diff = dim_inj_det - dim_oven;
    
    delayMicroseconds(dim_oven);
    digitalWrite(triac_oven,HIGH);
    delayMicroseconds(diff);
    digitalWrite(triac_inj_det,HIGH);
    delayMicroseconds(8.33 - diff);
    digitalWrite(triac_oven,LOW);
    delayMicroseconds(diff);
    digitalWrite(triac_inj_det,LOW); 
  }

  
}

void update_dimming(){
  dim_oven += 5;
  dim_inj_det;
  
}


void loop() {
  update_dimming();
  Serial.println(dim_oven);
  
}
