import threading

#Evento compartido para indicar que la grabación se inicio o se detuvo por parte del usuario.
recording_started_event = threading.Event()
 