from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
import traceback
from app.main import db
from app.models.catalogo import (CatCategoriasPlatillos)
from app.utils.response import api_response
from app.utils.RaiseException import (
    DatabaseError, MissingValueError, NotFoundError, UnexpectedError
)
from app.utils.Messages import (
            STATUS_CODE_200,STATUS_CODE_404,ERROR_EMPTY,
            SUCCESS,ERROR)
from app.utils.Logger import logger

LOG           = logger()
catalogos_bp  = Blueprint("catalogos", __name__)


# #####################################
# RUTAS PRIVADAS JWT
# #####################################
@catalogos_bp.route("/categorias-platillos", methods=["GET"])
@jwt_required()
def listar_categorias():
    try:
        id_categoria           = request.args.get("id_categoria")
        descripcion           = request.args.get("descripcion")

        query = CatCategoriasPlatillos.query.filter(CatCategoriasPlatillos.activo == 1)

        if id_categoria:
            query = query.filter(CatCategoriasPlatillos.id_categoria == id_categoria)
        
        if descripcion:
            query = query.filter(CatCategoriasPlatillos.descripcion.ilike(f"%{descripcion}%"))

        categorias = query.order_by(CatCategoriasPlatillos.id_categoria.asc()).all()
        
        if not categorias:
            LOG.warning(f"GET /categorias-platillos")
            return api_response(STATUS_CODE_404, None,ERROR,ERROR_EMPTY)

        LOG.info(f"GET /categorias-platillos — {len(categorias)} resultados")
        
        categorias_json = [c.to_dict() for c in categorias]
        
        return api_response(STATUS_CODE_200, categorias_json,SUCCESS)
    
    except SQLAlchemyError as e: 
        LOG.error(f"DB error en listar_categorias: {str(e)}")
        raise DatabaseError("Error al consultar la base de datos")
    except ValueError as e: 
        LOG.warning(f"Parámetro inválido: {str(e)}")
        raise UnexpectedError("Parámetros de búsqueda inválidos")
    except Exception as e:  
        error_trace = traceback.format_exc()
        LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
        raise UnexpectedError("Ocurrió un error inesperado")