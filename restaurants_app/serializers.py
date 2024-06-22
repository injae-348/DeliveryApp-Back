from rest_framework import serializers
from .models import Restaurant, Menu, MenuOption, Dib, MenuImage, Qrcode

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class MenuImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuImage
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    menu_images = MenuImageSerializer(many=True,read_only=True)
    class Meta:
        model = Menu
        fields = '__all__'

class MenuOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuOption
        fields = '__all__'

class DibSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dib
        fields = ['dibId','userId','storeId','status']

# QR 추가
class QrcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qrcode
        fields = '__all__'

