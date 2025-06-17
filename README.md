# Sistema de Pesaje de Fardos

## Configuración de la Balanza

El sistema está configurado para trabajar con una balanza conectada a través de un puerto serial. Para configurar la balanza:

1. Edita el archivo `funciones/config.json` con los parámetros de tu balanza:
   - `puerto`: Puerto COM al que está conectada la balanza (ej. COM1)
   - `baudrate`: Velocidad de comunicación (generalmente 9600)
   - `bytesize`: Tamaño de byte (generalmente 8)
   - `parity`: Paridad (none, even, odd, mark, space)
   - `stopbits`: Bits de parada (generalmente 1)
   - `timeout`: Tiempo de espera en segundos
   - `dtr` y `rts`: Configuración de control de flujo (generalmente true)

2. Asegúrate de que la balanza esté conectada al puerto configurado antes de iniciar el programa.

## Funcionamiento

El sistema lee continuamente el peso de la balanza y lo muestra en la interfaz. Para registrar un peso:

1. Ingresa el número de ticket
2. Ingresa el número de fardo inicial
3. Coloca el fardo en la balanza
4. Presiona Enter o el botón "PESAR" para registrar el peso

## Solución de problemas

Si tienes problemas con la conexión a la balanza:

1. Verifica que el puerto COM configurado sea el correcto
2. Asegúrate de que la balanza esté encendida y conectada
3. Comprueba que los parámetros de comunicación (baudrate, bytesize, etc.) coincidan con los de la balanza
4. Revisa los mensajes de error en la consola para obtener más información