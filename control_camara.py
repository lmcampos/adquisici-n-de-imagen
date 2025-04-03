import picamera
import threading
import time
import RPi.GPIO as GPIO
from  queue import Queue
from gpiozero import Button
from modulo_comun import recording_started_event

class ControlCamara(threading.Thread):
    def __init__ (self, grabacion_queue, pin,cola_log):
        super().__init__()
        self.camera = picamera.PiCamera()        
        #aquí configuro la camara segun las necesidades        
        self.camera.resolution = (640,480)
        self.camera.framerate = 120         
        self.grabacion_queue = grabacion_queue
        self.detener_hilo = threading.Event()
        self.numero_de_fotograma = 0
        self.pin = pin   
        #configuro el boton en el pin especificado
        #se configrua el pin 17 para interrupir al detectar flanco ascendente
        self.boton = Button(self.pin, pull_up = False)
        #asignar la devolución de llamada de evento de detección de un 1 lógico
        self.boton.when_pressed = self.capturar_datos_de_fotogramas
        #variables relacionadas a los fotogramas
        self.numero_de_fotograma = 0
        self.marca_de_tiempo = 0
        self.grabando = False 
        self.cola_log = cola_log
        self.index_de_fotograma = 0
        self.start_time = 0.0
        self.time_pin_aviso = 0.0
        #self.inicio_time_sistema = 0.0
        #self.inicio_time_camara_grabación = 0.0
        self.end_recording = 0.0
        # Pin para "avisar" al microcontrolador, en BCM 27
        self.pin_aviso = 27       
        # Configuramos RPi.GPIO para el pin_aviso
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_aviso, GPIO.OUT, initial=GPIO.LOW)

         
    def run(self):
        print ("hilo 2 - control Camara")
        while not self.detener_hilo.is_set():
            #print ("hilo 2 - me bloqueo para esperar un comando 'i' o 'd'")
            if not self.grabacion_queue.empty():
                comando = self.grabacion_queue.get()
                if comando == "iniciar":
                    #self.inicio_time_sistema = time.time()
                    #self.camera.start_preview()
                    self.camera.start_recording('video.h264')
                    #self.inicio_time_sistema_buffering = time.time() - self.inicio_time_sistema  
                    #self.inicio_time_camara_grabación = self.camera.frame.timestamp
                    self.start_time = time.time() 
                    self.grabando = True       
                    # para que se estabilice la grabación porque no me captura el primer frame.
                    # Además, quizas la camára no ha capturado un fotograma o no ha actualizado 
                    # su valor de timestamp. Esto ocurre cuando se inicia la grabación y, de inmediato, se intenta 
                    # acceder acceder a esa propiedad sin dar tiempo a que se incialice. 
                    time.sleep(0.1)
                    recording_started_event.set()             
                    
                     # Avisar al microcontrolador con un pulso de 0.5s
                     # que inicie la estimulación - Esto es cuando se realizaron pruebas 
                     # para verificar las capturas de marca de tiempo al iniciar el encendido de los leds 
                     # y se almacenaban dichas marcas de tiempo en el archivologs 
                    GPIO.output(self.pin_aviso, GPIO.HIGH)
                    self.time_pin_aviso = time.time() - self.start_time 
                    time.sleep(0.5)      # Esperar 0.5 segundos
                    GPIO.output(self.pin_aviso, GPIO.LOW)
                    #print("AVISO al micro: pin_aviso = LOW")

                else:
                    if comando == "detener":  
                        self.camera.stop_recording()
                        self.camera.stop_preview()
                        self.grabando = False             
                        self.end_recording = time.time()-self.start_time 
                        recording_started_event.clear()
                        print("tiempo de grabación:",self.end_recording)           
                    else:
                        if comando == "stop":
                            self.cerrar_hilo()     
                            
                           
            time.sleep(0.1)   

    def cerrar_hilo(self):
        self.camera.close()
        self.detener_hilo.set()   
    
    def capturar_datos_de_fotogramas(self):
        """
        Método que se llama automáticamente al detectar un flanco ascendente en pin 17.
        """
        if self.grabando:
            # Incrementar el contador de frames
            self.numero_de_fotograma += 1
            
            # Timestamp interno de la cámara (tiempo desde que inició la grabación)
            # Al invocar .frame.timestamp, picamera devuelve microsegundos desde el inicio de la grabación.
            # Si 'self.camera.frame' no está disponible en tu versión, usá time.time() o un approach similar.
            marca_de_tiempo_frame = self.camera.frame.timestamp/1000000
            self.index_de_fotograma = self.camera.frame.index

            delta_s = time.time() - self.start_time

            
            # Empaquetar datos en una lista
            metadatos = [
                self.numero_de_fotograma,    # N° de frame
                marca_de_tiempo_frame,       # Timestamp relativo a la grabación
                delta_s,       # Timestamp absoluto del sistema (opcional)
                self.index_de_fotograma,     # index fotograma asignado por la API de la cámara
                #self.inicio_time_sistema,  # tiempo absoluto antes de la instrucción preview
                self.start_time,          # toma del tiempo absoluto del inicio de la grabación
                #self.inicio_time_sistema_buffering, # tiempo abs que toma para ejecutar las instrucciones start_recording con API
                self.time_pin_aviso,       # tiempo en el que se avisa al micro que se inicia la grabación                    
            ]
            # Enviar al log
            # print ("envio a la cola log para almacenar la captura de marca de tiempo")
            self.cola_log.put(metadatos)
            

        
                
        
        
    

   


