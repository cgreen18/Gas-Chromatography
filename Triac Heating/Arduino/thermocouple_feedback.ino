int dig_out = 12;
int an_in = A0;

int dimming = 1024;


void setup() {
  Serial.begin(9600);
  pinMode(dig_out,OUTPUT);
  attachInterrupt(0, zero_cross_int, RISING);

}


void zero_cross_int(){
  int dimtime = 65*dimming;
  delayMicroseconds(dimtime);
  digitalWrite(dig_out,HIGH);
  delayMicroseconds(8.33);
  digitalWrite(dig_out,LOW);  // put your setup code here, to run once:
 
}

void loop() {
  while (true){
    Serial.println("here");
    dimming = analogRead(an_in);
    Serial.println(dimming);
  }
  

}
