

import logging
from typing import Dict, List
from ...applications.mcps.models import UserMCPConnection


class MCPManager:
    """
    El responsable de gestionar los MCPs (Módulos de Conexión de Proveedores) en la aplicación.
    """
    
    def __init__(self, user):
        self.user = user
        self.connection = self._load_connection()
        self.active_plugins = {}

    def _load_connection(self):
        """
        Carga la conexión del usuario desde la base de datos.
        
        Returns:
            Connection: La conexión del usuario.
        """
        return UserMCPConnection.objects.filter(
            user=self.user,
            status='active'
            ).select_related('mcp_provider__category')
    
    async  def initialize_plugins(self):
        """
        Inicializa los plugins activos del usuario.
        
        Returns:
            None
        """
        for connection in self.connection:
            try:
                plugin = connection.get_plugin()
                if await plugin.authenticate():
                    self.active_plugins[connection.mcp_provider.slug] = {
                        "plugin": plugin,
                        "connection": connection,
                        "methods": await plugin.get_available_methods()
                        }
            except Exception as e:
                logging.error(f"Error al inicializar el plugin {connection.mcp_provider.slug}: {e}")

    async def execute_claude_request(self, message:str, session_id:str) -> Dict:
        """
        Ejecuta una solicitud a Claude con el mensaje y la sesión proporcionados.
        
        Args:
            message (str): El mensaje a enviar a Claude.
            session_id (str): El ID de la sesión de Claude.
        
        Returns:
            Dict: La respuesta de Claude.
        """
        # Analiza el mensaje que determinar los MCP que necesita ejecutar.
        needed_mcp = await self._analyze_message_for_mcp(message)

        #Crear un contexto para la solicitud de Claude.
        context = await self._build_claude_context(needed_mcp)

        # Ejecutar la solicitud a Claude con el contexto.
        response = await self._send_claude_request(message, context)

        # Procesar la respuesta de Claude para extraer los resultados de los MCP.
        if response.get('mcp_calls'):
            mcp_resutls = await self._execute_mcp_calls(response['mcp_calls'])
            response['mcp_data'] = mcp_resutls
        
        return response
    
    async def _build_claude_context(self, needed_mcp: List[str]) -> Dict:
        """
        Construye el contexto para la solicitud de Claude basado en los MCP necesarios.
        
        Args:
            needed_mcp (List[str]): Lista de MCP necesarios.
        
        Returns:
            Dict: El contexto para la solicitud de Claude.
        """
        context = {
            'available_data_sources': [],
            'available_methods': {},
            'user_config': {}
        }

        for mcp_slug in needed_mcp:
            if mcp_slug in self.active_plugins:
                plugin_info = self.active_plugins[mcp_slug]
                context['available_data_sources'].append({
                    'name': plugin_info['connection'].mcp_provider.name,
                    'slug': mcp_slug,
                    'category': plugin_info['connection'].config_data
                })
                context['available_methods'][mcp_slug] = plugin_info['methods']
        return context