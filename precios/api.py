from rest_framework import viewsets, permissions

from . import serializers
from . import models


class MarcasViewSet(viewsets.ModelViewSet):
    """ViewSet for the Marcas class"""

    queryset = models.Marcas.objects.all()
    serializer_class = serializers.MarcasSerializer
    permission_classes = [permissions.IsAuthenticated]


class CorporationViewSet(viewsets.ModelViewSet):
    """ViewSet for the Corporation class"""

    queryset = models.Corporation.objects.all()
    serializer_class = serializers.CorporationSerializer
    permission_classes = [permissions.IsAuthenticated]


class ArticulosViewSet(viewsets.ModelViewSet):
    """ViewSet for the Articulos class"""

    queryset = models.Articulos.objects.all()
    serializer_class = serializers.ArticulosSerializer
    permission_classes = [permissions.IsAuthenticated]


class SiteViewSet(viewsets.ModelViewSet):
    """ViewSet for the Site class"""

    queryset = models.Site.objects.all()
    serializer_class = serializers.SiteSerializer
    permission_classes = [permissions.IsAuthenticated]


class SiteURLResultsViewSet(viewsets.ModelViewSet):
    """ViewSet for the SiteURLResults class"""

    queryset = models.SiteURLResults.objects.all()
    serializer_class = serializers.SiteURLResultsSerializer
    permission_classes = [permissions.IsAuthenticated]


class VendedoresViewSet(viewsets.ModelViewSet):
    """ViewSet for the Vendedores class"""

    queryset = models.Vendedores.objects.all()
    serializer_class = serializers.VendedoresSerializer
    permission_classes = [permissions.IsAuthenticated]


class PriceHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for the PriceHistory class"""

    queryset = models.PriceHistory.objects.all()
    serializer_class = serializers.PriceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]