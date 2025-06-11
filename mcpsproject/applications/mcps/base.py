from abc import ABC, abstractmethod #Define una clase base abstracta para las aplicaciones MCP
from typing import Any, Dict, List, Optional
import asyncio
import logging

class BaseApplication(ABC):
    """Esta es la clase base para todas las aplicaciones MCP.
    Proporciona una interfaz común y métodos básicos que deben ser implementados por todas las aplicaciones.
    """

    def __init__(self, credentials: Dict, config: Dict, user_id: str):
        self.credentials = credentials
        self.config = config
        self.user_id = user_id
        self.logger = logging.getLogger(f"mcp.{self.__class__.__name__}")

    #Usamos métodos abstractos para definir la interfaz que deben implementar las subclases.
    # Estos métodos no tienen implementación en esta clase base, pero deben ser implementados por las subclases concretas.
    # Las funciones asíncronas permiten que las subclases realicen operaciones de E/S sin bloquear el hilo principal, #lo que es útil para aplicaciones que interactúan con APIs externas o bases de datos.

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Método para autenticar la aplicación con las credenciales proporcionadas.
        Debe ser implementado por las subclases.
        """
        pass

    @abstractmethod
    async def get_available_methods(self) -> List[Dict]:
        """
        Método para obtener los métodos disponibles de la aplicación.
        Debe ser implementado por las subclases.
        """
        pass

    @abstractmethod
    async def execute_method(self, method_name: str, params: Dict) -> Dict:
        """
        Método para ejecutar un método específico de la aplicación.
        Debe ser implementado por las subclases.
        
        Args:
            method_name (str): El nombre del método a ejecutar.
            params (Dict): Los parámetros necesarios para el método.
        
        Returns:
            Any: El resultado de la ejecución del método.
        """
        pass

    async def refresh_token(self) -> bool:
        """
        Método para refrescar el token de autenticación.
        Por defecto, no hace nada, pero puede ser implementado por las subclases si es necesario.
        
        Returns:
            bool: True si el token se refrescó correctamente, False en caso contrario.
        """
        return True    
    
    def get_cache_key(self, method: str, params: Dict) -> str:
        """
        Método para generar una clave de caché basada en el nombre del método y los parámetros.
        
        Args:
            method (str): El nombre del método.
            params (Dict): Los parámetros del método.
        
        Returns:
            str: La clave de caché generada.
        """
        import hashlib
        # Genera un hash de los parámetros para crear una clave única
        key_data = f"{self.user_id}:{method}:{str(sorted(params.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
class AnalyticsMCPPlugin(BaseMCPPlugin):
    """Clase base para plugins de análisis de datos en MCP.
    Proporciona métodos comunes para la autenticación y ejecución de análisis.
    """

    @abstractmethod
    async def get_metrics(self, start_date: str, end_date: str, metrics: List[str], dimensions: List[str] = None) -> Dict:
        """
        Método para analizar datos específicos.
        Debe ser implementado por las subclases.
        
        Args:
            data (Any): Los datos a analizar.
        
        Returns:
            Any: El resultado del análisis.
        """
        pass

    @abstractmethod
    async def get_rea_time_data(self) -> Dict:
        """
        Método para obtener datos en tiempo real.
        Debe ser implementado por las subclases.
        
        Returns:
            Dict: Los datos en tiempo real obtenidos.
        """
        pass
class AdvertisingMCPPlugin(BaseMCPPlugin):
    """Clase base para plugins de publicidad en MCP.
    Proporciona métodos comunes para la autenticación y ejecución de campañas publicitarias.
    """

    @abstractmethod
    async def get_campaigns(self, status: str = 'active') -> List[Dict]:
        """
        Método para crear una campaña publicitaria.
        Debe ser implementado por las subclases.
        
        Args:
            status (Dict): Los estados de la campaña a crear.
        
        Returns:
            Dict:  Una lista de campañas publicitarias.
        """
        pass

    @abstractmethod
    async def get_campaigns_performance(self , campaign_ids: List[str]) -> List[Dict]:
        """
        Método para obtener las campañas publicitarias existentes.
        Debe ser implementado por las subclases.
        
        Returns:
            List[Dict]: Una lista de campañas publicitarias.
        """
        pass

    @abstractmethod
    async def get_account_performance(self) -> Dict:
        """
        Método para obtener el rendimiento de la cuenta publicitaria.
        Debe ser implementado por las subclases.
        
        Returns:
            Dict: El rendimiento de la cuenta publicitaria.
        """
        pass

