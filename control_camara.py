import picamera
import threading
import time
from  queue import Queue
from gpiozero import Button

class ControlCamara(threading.Thread):
    def __init__ (self, grabacion_queue, pin,cola_log):
        super().__init__()
        self.camera = picamera.PiCamera()        
        #aquí configuro la camara segun las necesidades        
        self.camera.resolution = (640,480)
        self.camera.framerate = 120         
        self.grabacion_queue = grabacion_queue
        self.detener_hilo = threading.Event()
        self.pin = pin   
        #configuro el boton en el pin especificado
        self.boton = Button(self.pin)
        #asignar la devolución de llamada de evento de detección de un 1 lógico
        self.boton.when_pressed = self.capturar_datos_de_fotogramas
        #variables relacionadasa los fotogramas
        self.numero_de_fotograma = 0
        self.marca_de_tiempo = 0
        self.grabando = False 
        self.cola_log = cola_log
         
    def run(self):
        print ("hilo 2 - control Camara")
        while not self.detener_hilo.is_set():
            print ("hilo 2 - me bloqueo para esperar un comando 'i' o 'd'")
            if not self.grabacion_queue.empty():
                comando = self.grabacion_queue.get()
                if comando == "iniciar":
                    self.camera.start_preview()
                    self.camera.start_recording('video.h264')
                    self.grabando = True                    
                else:
                    if comando == "detener":  
                        self.camera.stop_recording()
                        self.camera.stop_preview()
                        self.grabando = False                        
                    else:
                        if comando == "stop":
                            self.cerrar_hilo()     
            
            time.sleep(0.1)   

    def cerrar_hilo(self):
        self.camera.close()
        self.detener_hilo.set()   

    def capturar_datos_de_fotogramas(self):
        if self.grabando:
            metadatos = []
            self.numero_de_fotograma = self.camera.frame.index 
            self.marca_de_tiempo = self.camera.frame.timestamp
            metadatos.append(self.numero_de_fotograma)
            metadatos.append(self.marca_de_tiempo)                   
            self.cola_log.put(metadatos)
        
                
        
        
    

   


