from sqlalchemy.exc import SQLAlchemyError
from app.models.CatalogoModel import CatCategoriasPlatillos
from app.repositories.CatalogoRepository import CatalogoRepository
from app.utils.response import api_response
from app.utils.RaiseException import UnexpectedError
from app.utils.Logger import logger
import traceback
from app.utils.RaiseException import ( DatabaseError,  UnexpectedError)
from app.utils.Messages import *

LOG = logger()

class CatalogoService:
    @staticmethod
    def obtener_categorias_activas():
        try:
            # Obtenemos categorias activas
            categorias = CatalogoRepository.obtener_categorias_activas()
            
            if not categorias:
                LOG.warning(f"GET /categorias-platillos")
                return api_response(STATUS_CODE_404, None,ERROR,ERROR_EMPTY)

            LOG.info(f"GET /categorias-platillos {len(categorias)} resultados")
            categorias_json = [c.to_dict() for c in categorias]
            return api_response(STATUS_CODE_200,categorias_json,SUCCESS)
        except ValueError as e: 
            LOG.warning(f"Parámetro inválido: {str(e)}")
            raise UnexpectedError("Parámetros de búsqueda inválidos")
        except Exception as e:  
            error_trace = traceback.format_exc()
            LOG.error(f"Error inesperado: {str(e)} | Trace: {error_trace}")
            raise UnexpectedError("Ocurrió un error inesperado")