int inByte = 0;
byte trigger = 0;
void setup() {
  // put your setup code here, to run once:
pinMode(13,OUTPUT);
Serial.begin(9600);
while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only

}
}

void loop() {
  // put your main code here, to run repeatedly:
if (Serial.available() > 0) {
  digitalWrite(inByte,LOW);
  inByte = Serial.parseInt();
  digitalWrite(inByte,HIGH);
  trigger = 1;
}
if (trigger == 1){
Serial.println(inByte+1);
trigger = 0;
}

}

