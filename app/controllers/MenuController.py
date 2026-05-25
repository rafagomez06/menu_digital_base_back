from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.utils.Messages import *
from app.utils.Logger import logger
from app.services.MenuServices import MenuServices
LOG  = logger()
MenuController  = Blueprint("menu", __name__)

# #####################################
# Rutas publicas (sin JWT)
# #####################################

@MenuController.route("/platillos", methods=["GET"])
def obtener_platillos():
    return MenuServices.obtener_platillos()

# #####################################
# Rutas privadas (JWT)
# #####################################
@MenuController.route("/platillos", methods=["POST"])
@jwt_required()
def crear_platillo():
    data = request.form
    files = request.files
    return MenuServices.crear_platillo(data, files)

@MenuController.route("/platillos/<int:id_platillo>", methods=["PUT"])
@jwt_required()
def editar_platillo(id_platillo):
        data = request.form
        return MenuServices.editar_platillo(id_platillo, data)

@MenuController.route("/platillos/<int:id_platillo>", methods=["DELETE"])
@jwt_required()
def eliminar_platillo(id_platillo):
        return MenuServices.eliminar_platillo(id_platillo)    
        
