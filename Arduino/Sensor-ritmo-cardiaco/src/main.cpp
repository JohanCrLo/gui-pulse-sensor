#include <Arduino.h>
#include <pulseSensor.h>

//Declaración de variables
int sensorPulso = 0; //Pin analógico en donde se conectará el sensor
int LEDRED = 7; //Pin del led ver
int LEDGREEN = 8; //Pin del led rojo
int buzzer = 2; //Pin del zombador
int Signal; //Variable donde se alamcenará el valor leido del sensor
int Threshold = 520;  //Dato analogico considerado como un pulso (suele variar entre 400-600)
int option; //Variable encargada de encender el led rojo y verde
int option2; //Variable encargada de determinar si la GUI de python está activa para usar el buzzer

pulseSensor metodo(sensorPulso); //Inicialización del método de la biblioteca pulseSensor.h 

void setup() {
  //Se estable el modo de cada Pin, se abre el puerto serial y se enciende el led rojo y apaga el verde
  pinMode(LEDRED,OUTPUT);
  pinMode(LEDGREEN,OUTPUT);
  pinMode(buzzer,OUTPUT);
  digitalWrite(LEDRED, HIGH);
  digitalWrite(LEDGREEN, LOW);
  Serial.begin(9600);
}

void loop() {
  Signal = analogRead(sensorPulso);  //Lectura de datos del sensor de ritmo cardiaco
  Serial.println(Signal);            //Se muestro el valor de la señal en el puerto serie

  //Condicional encargado de ver si la GUI está en funcionamiento para encender los LED
  if (Serial.available()>0){
    option = Serial.read();  //Valor que se envia desde Python hacia arduino por el puerto serial
    Serial.println(option);
    if (option == 'y'){ //La opción 'P' determina que la GUI está activa
      digitalWrite(LEDGREEN, HIGH);
      digitalWrite(LEDRED, LOW);
      option2 = 'y'; //Se asigna el valor a option2 para activar el zumbador
    }
    if (option == 'z'){//La opción 'N determina que la GUI no está activa
      digitalWrite(LEDGREEN, LOW);
      digitalWrite(LEDRED, HIGH);
      option2 = 'z'; //Se asigna el valor a option2 para desactivar el zumbador
    }
  }

  metodo.buzzerActivation(Signal, Threshold, buzzer, option2); //Método encargado de activar el zumbador si la señal recibida es un pulso y la GUI está activa
  metodo.getBPMValue(Signal); //Método encargado de obtener las pulsaciones por minuto del usuario

  delay(100);
}