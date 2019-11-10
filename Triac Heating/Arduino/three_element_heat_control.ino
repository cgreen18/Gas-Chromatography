/*  Title: three_element_heat_control.ino
 *  Author: Conor Green and Matt McPartlan
 *  Description: Reads injector, detector, and oven amplified thermocouple analog voltages... 
 *    and converts the values to temperature in Celcius. PID loop implemented using current...
 *    and target temperature.
 *  Usage: Upload to microcontroller with interrupt capability. Arduino Pro Micro 5V used.
 *  Version:
 *    1.0 - November 9 - Initial creation.
 */

// Constants - put in header/cpp later
// Max error from: minimum temp ~ 30C & max temp desired ~ 180 & small margin
float ERR_MAX = 160.0

float K_P_OVEN = 0.5;
float K_I_OVEN = 0.2;
float K_D_OVEN = 0.2;

float K_P_INJ_DET = 0.5;
float K_I_INJ_DET = 0.2;
float K_D_INJ_DET = 0.2;

// Oven pins
int inter_oven = 2;
int triac_oven = 5;
int thermo_oven = A2;

// Oven variables (defaults)
int dim_oven = 1024;
float targ_oven = 100.0;
float temp_oven = 30.0;


// Injector and detector pins
int inter_inj_det = 3;
int triac_inj_det = 6;
int thermo_injector = A0;
int thermo_detector = A1;

// Injector and detector variables
int dim_inj = 1024;
int dim_det = 1024;
float targ_inj_det = 100.0;
float temp_inj = 30.0;
float temp_det = 30.0;

/*  Analog voltage to temperature conversion
 *  T = 58.3V + 39.2
 */

void setup() {
  pinMode(triac_inj_det,OUTPUT);
  pinMode(triac_oven,OUTPUT);
  attachInterrupt(digitalPinToInterrupt(inter_oven), zc_inter_oven, RISING);
  attachInterrupt(digitalPinToInterrupt(inter_inj_det), zc_inter_inj_det, RISING);
}

void zc_inter_oven(){
  delayMicroseconds(dim_oven);
  digitalWrite(triac_oven,HIGH);
  delayMicroseconds(8.33);
  digitalWrite(triac_oven,LOW); 
}

void zc_inter_inj_det(){
  delayMicroseconds(dim_inj_det);
  digitalWrite(triac_inj_det,HIGH);
  delayMicroseconds(8.33);
  digitalWrite(triac_inj_det,LOW); 
}

void update_temperatures(){
  dim_oven = analogRead(thermo_oven);
  temp_oven = .284667*dim_oven + 39.2;

  dim_inj = analogRead(thermo_inj);
  temp_inj = .284667*dim_inj + 39.2;

  dim_det = analogRead(thermo_det);
  temp_det = .284667*dim_det + 39.2;
}

void update_dimming(){
  float err, p, i, d, u;
  
  // Oven
  err = targ_oven - temp_oven;
  p = K_P_OVEN*err;
  i = K_I_OVEN*err;
  d = K_D_OVEN*err;

  u = p + i + d;
  dim_oven = (int) ((65.0*1024.0/ERR_MAX)*(ERR_MAX-err));

  // Injector and detector
  // Weighted average between injector and detector
  err = targ_inj_det - 0.2*temp_det - 0.8*temp_inj;

  p = K_P_OVEN*err;
  i = K_I_OVEN*err;
  d = K_D_OVEN*err;

  u = p + i + d;
  dim_inj_det = (int) ((65.0*1024.0/ERR_MAX)*(ERR_MAX-err));
}


void loop() {
  while (true){
    update_temperatures();
    update_dimming();
  }
}