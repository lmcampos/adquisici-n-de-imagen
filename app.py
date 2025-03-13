import threading
from queue import Queue
from control_camara import ControlCamara
from control_grabacion import ControlGrabacion
from envio_puerto_serie import EnvioPuertoSerie

from lectura_csv import LecturaCSV
from escritor_log import EscritorLog
import time
import serial


def main():
    #defino el pin por el que interrumpirá la EDU-CIAA-NXP (trigger)
    pin = 17 #pin físico 17

    #creo una cola para comunicar los hilos control_grabación y control_camara
    grabacion_queue = Queue()
    #Creo una cola para comunicar el hilo de control, de grabacióon y el hilo que escritor del archivo los
    cola_log = Queue()  
    #creo una cola para la comuniocación entre el hilo principal y el hilo control_grabación 
    cola_detener_todos_los_hilos = Queue()
    #Crea una cola para enviar los datos leidos del archivo CSV al Tx de puerto serie
    cola_envio = Queue()
    #creo una cola para comunicar los hilos puerto serie y lectura:  el hilo 
    #puerto serie comunica al de lectura que recibió un 'OK'
    data_queue = Queue()

    #crear una instancia/hilo de la clase ControlCamara
    hilo_control_camara = ControlCamara(grabacion_queue, pin, cola_log)
    #crear una instancia/hilo de la clase ControlGrabacion
    hilo_control_grabacion = ControlGrabacion(grabacion_queue,cola_detener_todos_los_hilos)
    
    #proporciono la ruta/nombre del archivo .csv
    mi_archivo_csv = "estimulaciones.csv"
    #Proporciona la ruta/nombre del "archivo_log.csv" que guarda los datos del fotograma
    mi_archivo_log_csv ="archivo_log.csv"
    
    #creo instancia del puerto serie
    puerto_serie = serial.Serial('/dev/ttyS0', 115200)
    #Crear una instancia/hilo de la clase EnvioPuertoSerie
    hilo_puerto_serie = EnvioPuertoSerie(puerto_serie,data_queue)
    #Crear una instancia/hilo de la clase LecturaCSV 
    hilo_lectura_csv = LecturaCSV(mi_archivo_csv, data_queue, hilo_puerto_serie)
    #Crear una instancia/hilo de la clase EscritorLog. Escribe los datos de fotogramas 
    hilo_escritor_de_log = EscritorLog(cola_log,mi_archivo_log_csv) 
    
    # inicio la ejecucuón de los hilos creados
    hilo_control_camara.start()
    hilo_control_grabacion.start()
    hilo_lectura_csv.start()
    hilo_puerto_serie.start()
    hilo_escritor_de_log.start()
    
    while True:
        if not cola_detener_todos_los_hilos.empty():
           if "detener" == cola_detener_todos_los_hilos.get():
                hilo_control_camara.cerrar_hilo()
                #aquí está demás cerrar el hilo control_grabación (input()) ya que en su 
                #clase lo cierro cuando se ingresa 'q'. Sino debo presionar doble enter al quedarse bloqueado en inputnuevamente  
                hilo_control_grabacion.cerrar_hilo() 
                hilo_lectura_csv.cerrar_hilo()
                hilo_puerto_serie.cerrar_hilo()
                hilo_escritor_de_log.cerrar_hilo()
                break
        time.sleep(0.1)
    

    
    #Espera a que los hilos se detengan
    print("Finalizando el hilo principal......")
    hilo_control_camara.join()
    print("hilo 2 - control camara: cerrado.")
    hilo_control_grabacion.join()
    print("hilo 1 - control grabación: cerrado.")
    hilo_lectura_csv.join()
    print("hilo 3 - lectura CSV: cerrado. ")
    hilo_puerto_serie.join()
    print("hilo 4 - puerto serie OK: cerrado.")
    hilo_escritor_de_log.join()
    print("hilo 5 - escritor del archivo log.")
    print("La aplicación se detuvo correctamente.") 
       

     
if __name__ == "__main__":
    main()
