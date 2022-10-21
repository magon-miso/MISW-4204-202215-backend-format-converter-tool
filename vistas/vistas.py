import os
from flask import request, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
from werkzeug.utils import secure_filename
#from sqlalchemy.exc import IntegrityError
#from sqlalchemy import or_, desc
from datetime import datetime
from pydub import AudioSegment

from modelos import db, Task, TaskSchema, User, UserSchema

task_schema = TaskSchema()
user_schema = UserSchema()


class VistaSignup(Resource):

    def post(self):        
        validacion = self.validateUser(request)
        if validacion is not None:
            return "Ya existe un usuario registrado con ese " + validacion, 400
        
        new_user = User(username=request.json["username"], 
                                password=request.json["password"], 
                                email=request.json["email"],
                                role="USER")
        db.session.add(new_user)
        user_created = db.session.query(User).filter(User.username.like(request.json["username"]), User.password.like(request.json["password"])).first()
        db.session.commit()
        token = create_access_token(identity=new_user.id,additional_claims={"role": new_user.role, "user": new_user.username})
        return {"mensaje": "usuario creado exitosamente", "token": token, "id": user_created.id}
    

    def validateUser(self, request):
        user_name = db.session.query(User).filter(User.username.like(request.json["username"])).first()
        if user_name is not None:
            return "identificador"
    
        user_email = db.session.query(User).filter(User.email.like(request.json["email"])).first()
        if user_email is not None:
            return "correo"


class VistaLogin(Resource):

    def post(self):
        user = User.query.filter(User.username == request.json["username"], User.password == request.json["password"]).first()
        db.session.commit()
        if user is None:
            return "El usuario no existe", 404
        else:
            token = create_access_token(identity=user.id, additional_claims={"role": user.role, "user": user.username})
            return {"mensaje": "Inicio de sesión exitoso", "token": token}


class VistaTasks(Resource):

    # listar todas las tareas de conversion de un usuario 
    # usuario debe proveer el token
    # servicio devuelve id tarea, nombre y extension archivo, extension a convertir, estado 
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        #print("vista-tasks-get user_id: ", user_id)
        tasks = db.session.query(Task).select_from(Task).filter(Task.user==user_id).all()
        return [task_schema.dump(t) for t in tasks]


    @jwt_required()
    def post(self):
        filename = None
        # if 'fileName' in request.files:
        if 'file' in request.files:
            #file = request.files['fileName']
            file = request.files['file']

            # f = request.files['fileName']
            # basepath = os.path.dirname (__ file__) # La ruta donde se encuentra el archivo actual
            # upload_path = os.path.join (basepath, 'static \ uploads', secure_filename (f.filename)) #Nota: Si no hay una carpeta, debe crearla primero, de lo contrario se le preguntará que no existe tal ruta
            # f.save(upload_path)
            
            # print("file.filename: ", file.filename)
            if file.filename:                
                #print("vista-tasks-post file.filename: ", file.filename)
                filename = secure_filename(file.filename)
                
                #print("vista-tasks-post secure_filename: ", filename)
                audio_dir = current_app.config['AUDIO_DIR']
                
                #print("vista-tasks-post audio_dir:", audio_dir)
                #os.makedirs(audio_dir, exist_ok=True)
                
                #print("vista-tasks-post os.makedirs")
                file_path = os.path.join(audio_dir, filename)
                
                file.save(file_path)
                print("file_path:", file_path)

                #user_id=current_user.id
                user_id = get_jwt_identity()
                new_task = Task(filename=filename, 
                                newformat=request.form["newFormat"],
                                user=user_id,
                                status="uploaded", 
                                upload_date=datetime.now())

                db.session.add(new_task)
                db.session.commit()

                print(str(datetime.now()) +" converter init")
                song = AudioSegment.from_mp3(file_path)
                print(str(datetime.now()) +" mp3 ...")
                song.export(file_path.replace(".mp3", ".ogg"), format="ogg") 
                print(str(datetime.now()) +" ogg ok")

                # song = AudioSegment.from_mp3(file_path)
                # print(str(datetime.now()) +" mp3 ...")
                # song.export(file_path.replace(".mp3", ".wav"), format="wav") 
                # print(str(datetime.now()) +" wav ok")

                # song = AudioSegment.from_mp3(file_path)
                # print(str(datetime.now()) +" mp3 ...")
                # song.export(file_path.replace(".mp3", ".wma"), format="wma") 
                # print(str(datetime.now()) +" wma ok")

                # song = AudioSegment.from_mp3(file_path)
                # print(str(datetime.now()) +" mp3 ...")
                # song.export(file_path.replace(".mp3", ".acc"), format="acc") 
                # print(str(datetime.now()) +" acc ok")

                return task_schema.dump(new_task)
            return "Task was not created - empty file", 400
        return "Task was not created - file missing", 400


class VistaTask(Resource):

    @jwt_required()
    def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))        

    @jwt_required()
    def delete(self, id_task):
        task = Task.query.get_or_404(id_task)
        db.session.delete(task)
        db.session.commit()
        return '', 204
