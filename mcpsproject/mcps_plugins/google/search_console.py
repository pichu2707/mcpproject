from typing import Dict, List, Any, Optional
from ...applications.mcps.base import BaseMCPPlugin
from googleapliclient.discovery import build
from google.auth.credentials import Credentials

class GoogleSearchConsoleMCP(BaseMCPPlugin):
    """
    Plugin para interactuar con Google Search Console.
    Proporciona métodos para obtener datos de rendimiento y cobertura de URL.
    """

    async def authenticate(self) -> bool:
        """
        Autentica el plugin utilizando las credenciales de Google.
        
        Returns:
            bool: True si la autenticación es exitosa, False en caso contrario.
        """
        try:
            creds = Credentials(**self.credentials)
            service = build('searchconsole', 'v1', credentials=creds)
            # Test con una llamada simple llamada
            sites  = service.sites().list().execute()
            return True
        except Exception as e:
            self.logger.error(f"Error durante la autentificación en GSC: {e}")
            return False
        

        async def get_available_methods(self) -> list[Dict]:
            """
            Obtiene los métodos disponibles del plugin.
            
            Returns:
                list: Lista de métodos disponibles.
            """
            return [
                {
                    "name": "get_search_analytics",
                    "description": "Obtiene datos de rendimiento de Google Search Console.",
                    "parameters": {
                        'site_url': 'Website URL',
                        'start_date': 'Fecha de inicio (YYYY-MM-DD)',
                        'end_date': 'Fecha de fin (YYYY-MM-DD)',
                        'dimensions': 'Dimensiones a incluir (ej. ["query", "page"])',
                        'row_limit': 'Límite de filas a retornar (opcional, por defecto 1000)',
                    }
                },
                {
                    "name": "get_top_pages",
                    "description": "Obtiene las páginas más relevantes del sitio web.", 
                    "parameters": {
                        'site_url': 'Website URL',
                        'start_date': 'Fecha de inicio (YYYY-MM-DD)',
                        'end_date': 'Fecha de fin (YYYY-MM-DD)',
                        'limit': 'Número de páginas a retornar (opcional, por defecto 10)',
                    }
                },
                {
                    "name": "get_top_queries",
                    "description": "Obtiene las consultas de búsqueda más relevantes.",
                    "parameters": {
                        'site_url': 'Website URL',
                        'start_date': 'Fecha de inicio (YYYY-MM-DD)',
                        'end_date': 'Fecha de fin (YYYY-MM-DD)',
                        'limit': 'Número de queries a retornar (opcional, por defecto 10)',
                    }

                }
            ]
        
    async def execute_method(self, method: str, params: Dict) -> Dict:
        """
        Ejecuta un método específico del plugin.
        
        Args:
            method (str): El nombre del método a ejecutar.
            params (Dict): Los parámetros necesarios para el método.
        
        Returns:
            Dict: Resultado de la ejecución del método.
        """
        if method == "get_search_analytics":
            return await self.get_search_analytics(**params)
        elif method == "get_top_pages":
            return await self.get_top_pages(**params)
        elif method == "get_top_queries":
            return await self.get_top_queries(**params)
        else:
            raise ValueError(f"Método {method} no implementado.")
        
    async def _get_search_analytics(self, site_url: str, start_date: str, end_date: str, dimensions: List[str], row_limit: Optional[int] = 1000) -> Dict:
        """
        Obtiene datos de rendimiento de Google Search Console.
        
        Args:
            site_url (str): URL del sitio web.
            start_date (str): Fecha de inicio en formato YYYY-MM-DD.
            end_date (str): Fecha de fin en formato YYYY-MM-DD.
            dimensions (List[str]): Dimensiones a incluir en la consulta.
            row_limit (Optional[int]): Límite de filas a retornar. Por defecto es 1000.
        
        Returns:
            Dict: Datos de rendimiento del sitio web.
        """
        creds = Credentials(**self.credentials)
        service = build('searchconsole', 'v1', credentials=creds)
        request_body = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': dimensions or ['page'],
            'rowLimit': row_limit
        }

        response = service.searchanalytics().query(
            siteUrl=site_url, 
            body=request_body
            ).execute()
        return response