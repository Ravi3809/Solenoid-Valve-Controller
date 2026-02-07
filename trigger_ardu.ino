const int Trigger_out=8;
void setup() {
  Serial.begin(9600);
  pinMode(Trigger_out, OUTPUT);
  digitalWrite(Trigger_out,LOW);
}

void loop() {
  if(Serial.available()>0){
    char command=Serial.read();
    if(command=='1'){
      digitalWrite(Trigger_out,HIGH);
    }
    else if(command=='0'){
      digitalWrite(Trigger_out,LOW);
    }
  }

}
