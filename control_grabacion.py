import threading
import picamera
import time
from queue import Queue


class ControlGrabacion(threading.Thread):

    def __init__(self,grabacion_queue,cola_detener_todos_los_hilos):
        super().__init__()
        self.grabacion_queue = grabacion_queue
        self.cola_detener_todos_los_hilos = cola_detener_todos_los_hilos
        self.detener_hilo = threading.Event()
        self.is_recording = False


    def run (self):
        print("hilo 1 - control grabación")
        while not self.detener_hilo.is_set():
            print("hilo 1 ")
            command = input("presione 'i' para iniciar grabación o 'd' para detener grabación").strip().lower()
            if command == 'i' and not self.is_recording:
                self.is_recording = True
                self.grabacion_queue.put("iniciar")
            else:
                if command == 'd' and self.is_recording:
                    print(command)
                    self.is_recording = False
                    self.grabacion_queue.put("detener")
                else:
                    if command == 'q':
                        self.cola_detener_todos_los_hilos.put("detener")
                        self.cerrar_hilo()
                       
            time.sleep(0.1)   
            
             
    def cerrar_hilo(self):
        self.detener_hilo.set()