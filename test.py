import matplotlib.pyplot as plt
import numpy as np

#Para graficar necesitamos unos datos
datos = np.arange(1,100,5)

#Generamos la figura y definimos el tamaño y la resolución
fig = plt.figure( figsize=(5,5), dpi = 100)

#La función plot nos permite dibujar líneas
#Si mandamos solamente un arreglo, matplotlib asume que el arreglo es la variable y y asigna automáticamente
#la x.
plt.plot(datos)

#Finalmente, mostramos la figura
plt.show()