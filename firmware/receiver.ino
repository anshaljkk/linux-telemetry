// arduino receiver for linux telemetry
// reads json from serial and lights up leds based on cpu %
//
// leds on pins 2,3,4,5,6 (5 leds = 5 bars of cpu load)
// each led = 20% cpu

String incoming = "";

void setup() {
    Serial.begin(9600);
    for(int i = 2; i <= 6; i++) {
        pinMode(i, OUTPUT);
    }
}

void loop() {
    while(Serial.available()) {
        char c = Serial.read();
        if(c == '\n') {
            process(incoming);
            incoming = "";
        } else {
            incoming += c;
        }
    }
}

void process(String s) {
    // really bad json parsing lol
    // just finding "cpu": and reading the number after it
    // should use a proper json library but ArduinoJson felt like overkill
    
    int idx = s.indexOf("\"cpu\":");
    if(idx == -1) return;
    
    float cpu = s.substring(idx + 6).toFloat();
    
    int leds = (int)(cpu / 20.0);
    if(leds > 5) leds = 5;
    
    for(int i = 0; i < 5; i++) {
        digitalWrite(i + 2, i < leds ? HIGH : LOW);
    }
}
