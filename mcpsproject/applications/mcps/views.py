from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

class MCPProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para manejar las operaciones relacionadas con los MCP Providers.
    """
   