#Importación de la librerias necesarias para el programa
from tkinter import *
from tkinter import messagebox
import collections
from datetime import datetime
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#from random import randrange
import serial
import time


#Se define que hoja de estilo de usará
plt.style.use('ggplot')

#Se declaran los "deques" en donde se almacenarán los datos
datax=collections.deque(maxlen=60) #Datos para el eje X (Hora actual)
datay=collections.deque(maxlen=60) #Datos para el eje Y (Señal del sensor de ritmo cardíaco)
dataBPM = collections.deque(maxlen=10) #Valores BPM obtenidos

aux = 0 #Variable auxiliar para inicializar los deques con un valor
#Almacenamiento de "aux" a cada uno de los deques. 
dataBPM.append(aux)


#Variables para la graficación con matplotlib
figure, ax = plt.subplots(facecolor='#05FFBF') #Se crea una figura y un conjunto de ejes
figure = plt.figure() #Se crea un objeto figura
line, = plt.plot_date(datax, datay, '-') #Módulo para el trazado de datos con fechas, en este caso, para la hora del eje X


#Función que adquiere los datos de ambos ejes para la gráfica
def grafica(frame):
    datax.append(datetime.now()) #Se almacena el tiempo actual el deque de X
    #datay.append(randrange(40,180))
    signal = int(arduino.readline()) #Se lee el dato enviado desde arduino, se convierte a entero y se almacena en una variable
    newY = tomardatos(signal) #Se ejecuto la función par saber si es un dato con posibilidad de graficado
    pulsos = tomardatos2(signal) #Se ejecuta la función para saber si es un dato perteneciente a las pulsaciones por minuto
    datay.append(newY) #Se agregan los datos con posibilidad de graficado al deque de Y
    dataBPM.append(pulsos) #Se agregan los datos pertenecientes a las pulsaciones por minuto al deque de BPM
    acutualizarDatos() #Función que actualiza los ejes de la grafica cada segundo
    #warning()
    line.set_data(datax, datay) #Se asignan las datos para los ejes
    figure.gca().relim(visible_only=True) #Recalcular los limites de los datos
    figure.gca().autoscale_view(scalex=True, scaley=True) #Se realiza el autoescalado de la gráfica
    return line,

#Función que se encarga de graficar los datos adquiridos una vez se presiona el botón "graficar datos", además de deshabilitar el botón susodicho
def iniciar():
    global ani
    ani = animation.FuncAnimation(figure, grafica, interval=200, blit=True, save_count=10) #Animación de la grafica para que se actualiza en tiempo real
    conexion() #Función encargada de saber si se reciben datos del puerto serial
    btniniciar.config(text='', background='white', border=0)
    btniniciar['state'] = 'disabled' #Se desactiva el botón "Gráficar datos" para evitar que se amontonen gráficas por erro
    canvas.draw() #Se dibuja la gráfica
    arduino.write(b'y') #Señal para encender el LED verde del Arduino y apagar el rojo

#Funciones encargadas de determinar si los datos pertenecen a señales del sensor o las pulsaciones por minuto
def tomardatos(signal):
    if signal > 110:
        return signal
    else:
        signal = datay[-1]
        return signal

def tomardatos2(signal):
    print(signal)
    if signal < 100:
        return signal
    else:
        bpm = dataBPM[-1]
        return bpm

#Función que actualiza los datos que se muestras en la interfaz, tanto de los ejes como el del último pulso leido y la advertencia que se muestra cuando se está por encima de las pulsaciones normales
def acutualizarDatos():
    #warning()
    pulse.config(text=f"BPM: {dataBPM[-1]}") #Actualización del dato de pulsaciones por minuto
    canvas.draw() #Se vuelve a dibujar la gráfica  


#Funcioón que pausa la graficación
def pausar():
    arduino.write(b'z') #Señal para encender el LED rojo del Arduino y apagar el verde
    ani.event_source.stop() #Función que detiene el graficado


#Función que reanuda la graficación
def reanudar():
    arduino.write(b'y') #Señal para encender el LED verde del Arduino y apagar el rojo
    ani.event_source.start() #Función que reanuda el graficado

def close():
    arduino.write(b'z') #Señal para encender el LED rojo del Arduino y apagar el verde
    ventana.destroy() #Función que cierra la ventana, es decir, cierra la interfaz de usuario


#Función encargada de comprobar la conexión entre python y arduino
def conexion():
    #Se eleva un error en caso de que el puerto no está activo
    try:
        arduino.open()
        print('Conexión exitosa')
    except:
        arduino.close()
        print('No se abrió el puerto')
        messagebox.showwarning(message='No se abrió el puerto', title='Error') #Mensaje de erro en la interfaz
        ventana.destroy() #Como el puerto no está activo, se cierra la interfaz


#Función que adquiere la edad ingresada en el Entry "age" y enviada con el Button "btnedad" para mostrar la frecuancia normal de acuerdo al valor adquirido
def enviarEdad():
    value = int(age.get()) #Se obtiena la edad colocado en al apartado de edad
    #arduino.write(b'P')
    btniniciar['state'] = 'normal' #Se activa el botón para poder graficar
    #Se envía el mensaje de la frecuencia cardíaca normal de acuerdo con la edad
    if value >= 10:
        result['text'] = 'La frecuencia cardiaca normal es de 60 a 100 BPM'
    elif value >= 7:
        result['text'] = 'La frecuencia cardiaca normal es de 70 a 110 BPM'
    elif value >=5:
        result['text'] = 'La frecuencia cardiaca normal es de 75 a 115 BPM'
    elif value > 2:
        result['text'] = 'La frecuencia cardiaca normal es de 80 a 130 BPM'
    elif value <= 2:
        result['text'] = 'La frecuencia cardiaca normal es de 70 a 190 BPM'


#Función que muestra un mensaje de advertencia en el Label "warningMsg" cuando se está por encima de la frecuancia normal de acuerdo con la edad ingresada
def warning():
    value = int(age.get())
    if value >= 10 and dataBPM[-1] > 110:
        warningMsg['text'] = 'Tu frecuencia está por encima de lo normal si es que NO estás haciendo alguna activadad física'
    else:
        warningMsg['text'] = ' '


#Inicializacón de variables concernientes a Tkinter y Pyserial para que el programa funcione
ventana = Tk() #Se establece un nombre para la interfaz principal
ventana.geometry('1200x1300') #Medidas de la interfaz 
ventana.title('Gráfica de ritmo cardíaco') #Título de la interfaz
ventana.minsize(width=1200, height=1300) #Medidad mínimas de la interfaz
arduino = serial.Serial() #Se inicia el puerto serie y se le asigna un nombre
arduino.baudrate=9600 #Baudios del puerto serie, debe coincidir con el de arduino
arduino.port='COM7' #Nombre del puerto seria al que Arduino está conectado
time.sleep(2)


#Declaración de los frames que serán usados en la interfaz, es decir, de las diferentes zonas que tandrá la interfaz y su posicionamiento
frame5 = Frame(ventana, bg = 'white', bd=3) #Frame5 muestra el titulo de la interfaz
frame5.pack(expand=1, fill='both', side='top')

frame3 = Frame(ventana, bg = 'white', bd=3) #Frame3 es en donde se coloca el Button y Entry para la edad 
frame3.pack(expand=1, fill='both', side='top')

frame4 = Frame(ventana, bg = 'white', bd=3) #Frame4 es en donde se coloca el mensaje de advertencia para pulsaciones fuera de lo normal
frame4.pack(expand=1, fill='both', side='top')

frame = Frame(ventana, bg='white', bd=3) #Frame es en donde se colocan los botonos relacionados con el graficado de la interfaz
frame.pack(expand=1, fill='both', side='top')

frame2 = Frame(ventana, bg='white', bd=3) #Frame2 es donde se coloca el texto con la última pulsación recibida
frame2.pack(expand=1, fill='both', side='bottom')

canvas = FigureCanvasTkAgg(figure, master=ventana)
canvas.get_tk_widget().pack(padx=5,pady=5,expand=1, fill='both')


#Declaración, diseño, colocación y función de todos los Label´s y Button´s de la interfaz
startMsg = Label(frame5, text='Para iniciar debes ingresar tu edad' ,bg='white', fg='black', font=('Arial', 20))
startMsg.pack(pady=5, side = 'left', expand=0)

ageMsg = Label(frame3, text='Ingresa tu edad (años)',bg='white', fg='black', font=('Arial', 15))
ageMsg.pack(pady=5, side = 'left', expand=0)

age = Entry(frame3, text='Ingresa tu edad (años)' ,width=18,font=('Arial', 15), relief='raised', bg='white',highlightbackground='blue' ,highlightthickness=3)
age.pack(pady=5, side='left', expand=0)

btnedad = Button(frame3, text='Enviar edad',width=15, bg='blue',fg='white', font=('Arial', 15), foreground='white', command=enviarEdad)
btnedad.pack(pady=5, side='left', expand=0)

result = Label(frame4, text='     ', bg='white', fg='black', font=('arial', 17))
result.pack(pady=5, side='right', expand=0)

warningMsg = Label(frame4, text='     ', bg='white', fg='red4', font=('arial', 14))
warningMsg.pack(pady=5, side='bottom', expand=1)

pulse=Label(frame2, text='BPM: ', font=('Arial', 20))
pulse.pack(pady=5, side='left', expand=0)

btniniciar = Button(frame, text='Grafica datos',width=15, bg='purple3', fg='white', font=('Arial', 15), foreground='white',command=iniciar, state=DISABLED)
btniniciar.pack(pady=5, side='bottom',expand=1)

btnpausar = Button(frame, text='Pausar',width=15, bg='gray', fg='white', font=('Arial', 15), foreground='white', command=pausar)
btnpausar.pack(pady=5, side='left',expand=1)

btncontinuar = Button(frame, text='Reanudar',width=15, bg='green4', fg='white', font=('Arial', 15), foreground='white', command=reanudar)
btncontinuar.pack(pady=5, side='left',expand=1)

btnterminar = Button(frame, text='Cerrar',width=15, bg='Red2', fg='white', font=('Arial', 15), foreground='white', command = close)
btnterminar.pack(pady=5, side='left', expand=1)


#Actualización y creación de la interfaz
ventana.after(1000, acutualizarDatos)
ventana.mainloop()

#Se cierra el puerto serie
arduino.close()