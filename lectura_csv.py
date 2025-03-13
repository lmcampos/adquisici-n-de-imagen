import csv
import threading
from queue import Queue
import queue
import time
from modulo_comun import recording_started_event

class LecturaCSV(threading.Thread):
    #data_queue cola que espera el "OK"
    #cola_envio es la cola por la que enviamos cada linea del archivo al puerto serie
    def __init__(self, archivo_csv, data_queue,hilo_puerto_serie):
        super().__init__()
        self.archivo_csv = archivo_csv
        self.data_queue = data_queue # cola donde sereciben los ACK_DONE
        self.hilo_puerto_serie = hilo_puerto_serie # instancia del hilo de envío
        #self.cola_envio = cola_envio
        self.detener_hilo = threading.Event()

               

    def run(self):
        print("inicio el hilo_lectura CSV.")
        
        comandos = []
        with open(self.archivo_csv,newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0].strip().upper() in ("EOF", "END"):
                    print("Marcador de fin encontrado en CSV. No se leerán más comandos.")
                    break
                # Reconstruye la línea y añade el salto de línea al final.
                comando = ",".join(row) + "\n"
                comandos.append(comando)
        total = len(comandos)
        print(f"Se han leído {total} comandos desde {self.archivo_csv}.")
        if total == 0:
            self.detener_hilo.set()
            return
        sent_count = 0
        ack_count = 0
        
        # aqui debo recibir una señal de que se inicio la grabación
        # para enviar las primeras dos estimulaciones

        # aquí se bloquea el hilo hasta que active el evento. 
        # Es decir, cuando se inicia la grabación
        recording_started_event.wait()

        # Envía los dos primeros comandos.
        if total >= 1:
            self.hilo_puerto_serie.enviar_fila(comandos[0])
            sent_count += 1
        if total >= 2:
            self.hilo_puerto_serie.enviar_fila(comandos[1])
            sent_count += 1
        siguiente = 2  # Índice del siguiente comando a enviar.

        # Bucle principal: cada vez que se recibe un ACK_DONE, envía el siguiente comando.
        while not self.detener_hilo.is_set():
            try:
                ack = self.data_queue.get(timeout=1)
                if ack.strip().startswith("ACK_DONE"):
                    print(f"ACK recibido: {ack}")
                    ack_count += 1
                    if siguiente < total:
                        self.hilo_puerto_serie.enviar_fila(comandos[siguiente])
                        sent_count += 1
                        siguiente += 1
                else:
                    print(f"Respuesta inesperada: {ack}")
                # Si se han recibido ACK para todos los comandos, terminamos.
                if ack_count >= total:
                    print("Todos los comandos han sido enviados y confirmados.")
                    self.detener_hilo.set()
            except Exception:
                # Timeout, continúa esperando.
                pass
            time.sleep(0.1)
        print("Fin del hilo de lectura CSV.")
        print(f"Comandos enviados: {sent_count}, ACK recibidos: {ack_count}")
                
                
                
    def cerrar_hilo(self):
        self.detener_hilo.set()