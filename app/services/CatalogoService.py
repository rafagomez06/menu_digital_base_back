from sqlalchemy.exc import SQLAlchemyError
from app.models.catalogo import CatCategoriasPlatillos
from app.utils.response import api_response
from app.utils.RaiseException import UnexpectedError
from app.utils.Logger import logger
import traceback
from app.utils.RaiseException import ( DatabaseError,  UnexpectedError)
from app.utils.Messages import *

LOG = logger()

class CatalogoService:
    @staticmethod
    def listar_categorias():
        try:

            query = CatCategoriasPlatillos.query.filter(CatCategoriasPlatillos.activo == 1)
            categorias = query.order_by(CatCategoriasPlatillos.id_categoria.asc()).all()
            
            if not categorias:
                LOG.warning(f"GET /categorias-platillos")
                return api_response(STATUS_CODE_404, None,ERROR,ERROR_EMPTY)

            LOG.info(f"GET /categorias-platillos — {len(categorias)} resultados")
            categorias_json = [c.to_dict() for c in categorias]
            
            return api_response(STATUS_CODE_200,categorias_json,SUCCESS)
        
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