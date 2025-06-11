from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json
from cryptography.fernet import Fernet
from django.conf import settings

User = get_user_model()

class MCPCategory(models.Model):
    """
    Modelo para representar una categoría de MCPS (Modelo de Clasificación de Productos y Servicios).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    
class MCPProvider(models.Model):
    """Registro de toso lso MCPs dispobibles.

    Args:
        models (_type_): Nos permite crear un modelo de base de datos.
    """
    INTEGRATION_TYPES = [
        ('rest_api', 'REST API'),
        ('soap_api', 'SOAP API'),
        ('oauth2', 'OAuth 2.0'),
        ('api_key', 'API Key'),
        ('webhook', 'Webhook'),
        ('custom', 'Custom Integration'),
    ]

    PLAN_REQUIREMENTS = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]

    # Información básica del MCP
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(MCPCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    icon_url = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)

    # Configuración de la integración 
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    plugin_class = models.CharField(max_length=200)
    required_scopes = models.JSONField(default=list)
    webhook_events = models.JSONField(default=list)

    # Metadatos de la integración
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_plugin_instance(self):
        """
        Obtiene una instancia del plugin de integración.
        """
        module_path, class_name = self.plugin_class.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    
class UserMCPConnection(models.Model):
    """Usuario y conexión de MCP.
    Esta clase representa la conexión de un usuario a un MCP específico.

    Args:
        models (_type_): Nos permite crear un modelo de base de datos.
        user (User): El usuario que realiza la conexión.
    """

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('error', 'Error'),
        ('disabled', 'Disabled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mcp_provider = models.ForeignKey(MCPProvider, on_delete=models.CASCADE)

    # Estado de la conexión
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Credenciales de la conexión encriptadas
    encrypted_credentials = models.TextField() # Encrypted JSON string

    # Metadatos de la conexión
    display_name = models.CharField(max_length=200, blank=True, null=True) # Nombre para mostrar
    config_data = models.JSONField(default=dict) # Configuración adicional en formato JSON
    last_sync = models.DateTimeField(null=True)
    sync_frequency = models.IntegerField(default=3600)  # En segundos

    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)

    class Meta:
        unique_together = ['user', 'mcp_provider','display_name']

    @property
    def credentials(self):
        """
        Desencripta las credenciales almacenadas.
        """
        if not self.encrypted_credentials:
            return {}
        fernet = Fernet(settings.SECRET_KEY.encode())
        decrypted = fernet.decrypt(self.encrypted_credentials.encode())
        return json.loads(decrypted.decode())
    
    @credentials.setter
    def credentials(self, value):
        """
        Encripta las credenciales antes de almacenarlas.
        """
        fernet = Fernet(settings.SECRET_KEY.encode())
        encrypted = fernet.encrypt(json.dumps(value).encode())
        self.encrypted_credentials = encrypted.decode()

    def get_plugin(self):
        """
        Obtiene una instancia del plugin de integración del MCP.
        """
        plugin_class = self.mcp_provider.get_plugin_instance()
        return plugin_class(
            credentials=self.credentials,
            config=self.config_data,
            user_id=self.user.id,
        )