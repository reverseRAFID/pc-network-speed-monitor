#include <LiquidCrystal.h>

LiquidCrystal lcd(7, 6, 5, 4, 3, 2);

void setup() {
  lcd.begin(16, 2);
  lcd.print("Internet Speed");
  delay(2000);
  lcd.clear();
  Serial.begin(9600); // Start Serial communication
}

void loop() {
  // Read data sent from Python script
  if (Serial.available() >= 3) {
    char data_type = Serial.read();
    String data_value = Serial.readStringUntil('\n');

    // Convert data_value to float
    float speed = data_value.toFloat();

    // Check the data type and display the speed accordingly
    if (data_type == 'T') {
      lcd.setCursor(0, 0);
      lcd.print("Tx: ");
      lcd.print(speed, 2); // Display with 2 decimal places
      lcd.print(" Mbps    ");
    } else if (data_type == 'R') {
      lcd.setCursor(0, 1);
      lcd.print("Rx: ");
      lcd.print(speed, 2); // Display with 2 decimal places
      lcd.print(" Mbps    ");
    }
  }
}
