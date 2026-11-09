const int TEST_PIN = 16; 

void setup() {
  // Inicializar o pino de teste como saída
  pinMode(TEST_PIN, OUTPUT);
}

void loop() {
  // Ligar o pino de teste (3,3 V)
  digitalWrite(TEST_PIN, HIGH);
  delay(1000); // Esperar 1 segundo

  // Desligar o pino de teste (0 V)
  digitalWrite(TEST_PIN, LOW);
  delay(1000); // Esperar 1 segundo
}