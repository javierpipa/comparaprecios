from rest_framework import serializers
from rest_framework.decorators import api_view, throttle_classes
from . import models


# @api_view(['GET'])
class MarcasSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Marcas
        fields = [
            
            "nombre",
            
        ]

class CorporationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Corporation
        fields = [
            "nombre",
        ]

class ArticulosSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Articulos
        fields = [
            "nombre",
            "nombre_original",
        ]

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Site
        fields = [
            "siteName",
            "corporacion",
            "account",
            "siteURL",
        ]

class SiteURLResultsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SiteURLResults
        fields = [
            "created",
            "last_updated",
            "precio",
        ]

class VendedoresSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Vendedores
        fields = [
            "created",
            "last_updated",
        ]

class PriceHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PriceHistory
        fields = [
            "Oldprecio",
            "OldDate",
        ]