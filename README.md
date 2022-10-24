
# Backend format converter tool
## Grupo MISW-4204-202215

Aplicación web para que usuarios de internet puedan subir abiertamente diferentes formatos multimedia de archivos y cambiarles su formato o realizar procesos de compresión

## Descripción

El modelo general de funcionamiento de la aplicación se basa en crear una cuenta en el portal web y acceder al administrador de archivos. Una vez la cuenta ha sido creada, el usuario puede subir archivos y solicitar el cambio de formato de estos para descargarlos. La aplicación web le permite a un usuario convertir archivos multimedia en línea de un formato a otro, seleccionando únicamente el formato destino.

Inicialmente, la aplicación permite convertir entre los formatos de audio: ```MP3 - OGG - WAV```. Para la conversion de formatos de audio se utiliza la libreria ```pydub``` https://github.com/jiaaro/pydub/, la cual requiere, para trabajar con archivos no-wav, instalar ```ffmpeg``` y configurar el ejecutable en el path https://www.gyan.dev/ffmpeg/builds/

## Inciando

### Dependencias

* Docker compose
* Windows, Linux, Mac

### Instalación

Para la ejecución del proyecto escribir la siguiente linea en la consola de comandos y teclear enter
```
docker-compose up -d --build
```
### Instalación y ejecución
Se debe descargar el código fuente con el siguiente comando
```
git clone https://github.com/magon-miso/MISW-4204-202215-backend-format-converter-tool.git
```

Se debe corroborar que docker se este ejecutando en el sistema operativo para lanzar la siguiente línea desda la consola de comandos
```
docker-compose up -d --build
```

La información sobre el consumo de los servicios expuestos se puede consultar en [Documentación API - Postman](https://documenter.getpostman.com/view/24011777/2s84DoT41R)