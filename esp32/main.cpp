#include <Arduino.h>
#include <WiFi.h>

const char *SSID = "Martian";
const char *PASSWORD = "123123123";
WiFiServer server(80);
// Motor A
int enA = 13;
int in1 = 12;
int in2 = 14;

// Motor B
int enB = 33;
int in3 = 26;
int in4 = 25;

void setup()
{
  Serial.begin(115200);
  delay(10);

  // --- KEHUBUNG KE WIFI
  WiFi.begin(SSID, PASSWORD);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println(WiFi.localIP());
  server.begin();
  Serial.println("Server started");
  // Set the motor control pins to outputs
  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
}

void moveForward()
{
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enA, 130); // Adjust the speed as needed
  analogWrite(enB, 126); // Adjust the speed as needed
}

void moveBackward()
{
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(enA, 255); // Adjust the speed as needed
  analogWrite(enB, 255); // Adjust the speed as needed
}

void turnLeft()
{
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enA, 0);   // Adjust the speed as needed
  analogWrite(enB, 125); // Adjust the speed as needed
}

void turnRight()
{
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(enB, 0);   // Adjust the speed as needed
  analogWrite(enA, 125); // Adjust the speed as needed
}

void stopMotors()
{
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);

  analogWrite(enA, 0);
  analogWrite(enB, 0);
}

void loop()
{

  WiFiClient client = server.available();

  if (client)
  {
    Serial.println("New client connected");

    // --- BACA DATA DARI CLIENT
    String data = client.readStringUntil('\r');
    data.trim();

    // --- PROSES DATA
    Serial.print("Received data: ");
    Serial.println(data);

    if (data.toInt() == 1)
    {
      Serial.println("majuuuu");
      // moveForward();
      // delay(500);
      // stopMotors();
      // delay(delayMotor);
      moveForward();
      delay(590);
      stopMotors();
      delay(500);
    }
    else if (data.toInt() == 3)
    {
      Serial.println("kanan");
      // turnRight();
      // delay(300);
      // stopMotors();
      // delay(delayMotor);
      turnRight();
      delay(630);
      stopMotors();
      delay(1000);
    }
    else if (data.toInt() == 2)
    {
      Serial.println("Kiri");
      // turnLeft();
      // delay(300);
      // stop();
      // delay(delayMotor);
      turnLeft();
      delay(630);
      stopMotors();
      delay(1000);
    }
    else if (data.toInt() == 0)
    {
      Serial.println("Berhenti");
      stopMotors();
      client.print(data);
      client.stop();
      return;
    }

    // --- KIRIM BALIK RESPONSE KE PYTHON
    client.print(data);

    // --- TUTUP KONEKSI
    client.stop();
    Serial.println("Client disconnected");
  }
  // Move forward

  // Move backward
  // moveBackward();
  // delay(2000);

  // Turn left

  // Move forward
  // moveForward();
  // delay(500);

  // // Turn right

  // // Stop
  // stopMotors();
  // delay(500);
}