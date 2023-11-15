import threading
import time
from queue import Queue
import csv

class EscritorLog(threading.Thread):
    
    def __init__(self,cola_log,mi_archivo_log_csv):
        super().__init__()
        self.cola_log = cola_log
        self.detener_hilo = threading.Event()
        self.mi_archivo_log_csv = mi_archivo_log_csv 
    
    def run(self):        
        with open (self.mi_archivo_log_csv, "w", newline = '' ) as archivo:
            escritura_csv = csv.writer(archivo,delimiter = ',')
            escritura_csv.writerow(['Número de Fotograma','Marca de Tiempo'])
        
            while not self.detener_hilo.is_set():
                print("hilo 5 - Escribo en el archivo Log. ")
                if not self.cola_log.empty():
                    dato_log = self.cola_log.get()
                    print(dato_log)   
                    escritura_csv.writerow(dato_log)             

                time.sleep(0.1)

    def cerrar_hilo(self):
        self.detener_hilo.set()        