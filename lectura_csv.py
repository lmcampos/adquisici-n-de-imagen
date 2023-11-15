import csv
import threading
from queue import Queue
import queue
import time

class LecturaCSV(threading.Thread):
    #data_queue cola que espera el "OK"
    #cola_envio es la cola por la que enviamos cada linea del archivo al puerto serie
    def __init__(self, archivo_csv, data_queue,hilo_puerto_serie):
        super().__init__()
        self.archivo_csv = archivo_csv
        self.data_queue = data_queue
        self.hilo_puerto_serie = hilo_puerto_serie
        #self.cola_envio = cola_envio
        self.detener_hilo = threading.Event()

               

    def run(self):
        print("inicio el hilo_lectura.")
        with open(self.archivo_csv,'r') as archivo:

            while not self.detener_hilo.is_set():
                
                
                print ("hilo 3 - lectura: me bloqueo para la espera del OK. ")
                if not self.data_queue.empty():
                    rx_ok = self.data_queue.get()
                    if rx_ok == "OK":
                        fila = archivo.readline()
                        self.hilo_puerto_serie.enviar_fila(fila)
                        if not fila:
                            self.cerrar_hilo() # si no hay más fila en el archivo termina el bucle
                            print("suspendo el hilo porque se termino el archivo")
                                        
                time.sleep(0.1)

    def cerrar_hilo(self):
        self.detener_hilo.set()