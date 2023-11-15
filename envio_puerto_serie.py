import serial
import threading
import time
import queue

class EnvioPuertoSerie(threading.Thread):

    def __init__(self, puerto_serie,data_queue):
        super().__init__()
        self.puerto_serie = puerto_serie
        self.data_queue = data_queue
        self.detener_hilo = threading.Event() 

            
    def run(self):
        print("inicio hilo 4: recepción OK")
        while not self.detener_hilo.is_set():
            print("hilo 4 - espera por el OK.")
            #verificar que se queda bloqueado y no sepuede finalizar 
            #este hilo y la aplicación correctamente
            if self.puerto_serie.inWaiting()>0:
                respuesta = self.puerto_serie.read(2).decode()
                if respuesta == "OK":
                    self.data_queue.put("OK")
            time.sleep(0.1)    
        
    def enviar_fila(self,dato):
        self.puerto_serie.write(dato.encode())
            
    def cerrar_hilo(self):
        self.detener_hilo.set()
