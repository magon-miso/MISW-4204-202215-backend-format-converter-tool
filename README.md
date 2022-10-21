# MISW-4204-202215-backend-format-converter-tool
Aplicación web para que usuarios de internet puedan subir abiertamente diferentes formatos multimedia de archivos y cambiarles su formato o realizar procesos de compresión

El modelo general de funcionamiento de la aplicación se basa en crear una cuenta en el portal web y acceder al administrador de archivos. Una vez la cuenta ha sido creada, el usuario puede subir archivos y solicitar el cambio de formato de estos para descargarlos. La aplicación web le permite a un usuario convertir archivos multimedia en línea de un formato a otro, seleccionando únicamente el formato destino.

Inicialmente, la aplicación permite convertir entre los formatos de audio: MP3 - ACC - OGG - WAV – WMA


Dependencias: para la conversion de formatos de audio se utiliza la libreria pydub https://github.com/jiaaro/pydub/, la cual requiere, para trabajar con archivos no-wav, instalar ffmpeg y configurar el ejecutable en el path https://www.gyan.dev/ffmpeg/builds/
