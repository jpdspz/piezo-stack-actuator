/*
 * Two-pin capacitance measurement for piezo stack
 * 
 * Pin D9  = charge/discharge output
 * Pin A0 = analog input to measure voltage
 * Resistor = 50 kΩ (five 10kΩ in series)
 * 
 * Measures discharge time from 5 V to 2.5 V (half voltage)
 * Calculates capacitance using C = t / (R * ln(2))
 */

const int chargePin = 9;          // Pin A: output for charging/discharging
const int measurePin = A0;        // Pin B: analog input (always input)

const float C_single = 32e-9;     // average capacitance of a single piezo (experimentally assessed)
const float R = 50000.0;          // 50 kΩ in ohms
const float ln2 = 0.693147;       // natural log of 2
const int threshold = 512;        // 2.5V on 5V ADC (1024 / 2)

const int numMeasurements = 10;   // number of measurements to average
const float timeoutSec = 1.0;     // safety timeout (seconds)

void setup() {
  Serial.begin(9600);
  pinMode(chargePin, OUTPUT);
  pinMode(measurePin, INPUT);
  digitalWrite(chargePin, LOW);   // start discharged
  
  Serial.println("Piezo capacitance test");
  /*
  Serial.print("Resistor: ");
  Serial.print(R / 1000.0);
  Serial.println(" kOhm");*/
  Serial.print("Averaging over ");
  Serial.print(numMeasurements);
  Serial.println(" measurements");
  Serial.println();
}

/*
 * Measures capacitance of the connected piezo based on the time it takes to discharge
 * Returns capacitance in farads (F)
 * Returns 0 if timeout or error
 */
float measureCapacitance() {
  // ----- Charge the piezo -----
  digitalWrite(chargePin, HIGH);    // 5V output
  delay(500);                       // plenty of time to charge (5τ = 62.5ms, so 500ms is safe)
  
  // ----- Start discharge and timing -----
  digitalWrite(chargePin, LOW);     // discharge through resistor to 0V
  
  unsigned long start = micros();
  unsigned long timeout = (unsigned long)(timeoutSec * 1000000.0);
  
  // Wait for voltage to drop below threshold (2.5V)
    while (analogRead(measurePin) > threshold) {
      if (micros() - start > timeout) {
        Serial.println("Timeout: piezo not discharging correctly");
        return;
      }
    }
  
  unsigned long elapsed = micros() - start;
  float t_sec = elapsed / 1000000.0;
  
  // Calculate capacitance: C = t / (R * ln(2))
  float capacitance = t_sec / (R * ln2);
  
  // Print individual measurement
  Serial.print("t = ");
  Serial.print(elapsed);
  Serial.print(" µs, C = ");
  Serial.print(capacitance * 1e9, 1);
  Serial.println(" nF");
  
  return capacitance;
}

void loop() {
  // Average multiple measurements
  float totalCap = 0;
  int validMeasures = 0;
  
  for (int i = 0; i < numMeasurements; i++) {
    float cap = measureCapacitance();
    if (cap > 0) {
      totalCap += cap;
      validMeasures++;
    }
    delay(500);   // short pause between measurements
  }
  
  if (validMeasures > 0) {
    float avgCap = totalCap / validMeasures;
    
    Serial.print("Average capacitance: ");
    Serial.print(avgCap * 1e9, 1);
    Serial.print(" nF (");
    Serial.print(avgCap * 1e6, 2);
    Serial.println(" uF)");
    
    // Estimate number of layers (if each ~5nF)
    float estLayers = avgCap / C_single;
    Serial.print("Estimated working layers: ");
    Serial.println(estLayers, 0);
  } else {
    Serial.println("No valid measurements");
  }
  
  Serial.println("---Test complete---");
  Serial.println("Type anything and press Enter to run again.");
  
  // Wait for user input to restart
  while (!Serial.available()) {
    // wait
  }
  
  // Small delay to let all characters arrive
  delay(100);

  // Clear the serial buffer
  while (Serial.available()) {
    Serial.read();
  }
  
  Serial.println("\n\nRestarting test...\n");
  delay(500);  // brief pause before restart
  // loop() will now run again automatically
}
