from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.utils.Messages import *
from app.utils.Logger import logger
from app.services.CatalogoService import CatalogoService

LOG = logger()
CatalogoController  = Blueprint("catalogos", __name__)

# #####################################
# Rutas privadas (JWT)
# #####################################

@CatalogoController.route("/categorias-platillos", methods=["GET"])
@jwt_required()
def listar_categorias():
    return CatalogoService.listar_categorias()
