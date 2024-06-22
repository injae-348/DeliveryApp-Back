# User 부분을 CutomUser로 바꿔주고 필드 채워주기
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate

from .models import CustomUser,Address,Reward

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required = True,
        validators = [UniqueValidator(queryset=CustomUser.objects.all())],
    )
    password = serializers.CharField(
        write_only=True,
        validators = [UniqueValidator(queryset = CustomUser.objects.all())],
    )
    password2 = serializers.CharField(write_only = True, required=True)
    is_restaurant_admin = serializers.BooleanField(default=False)

    class Meta:
        model = CustomUser
        fields = ('username','password','password2','email','is_restaurant_admin')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password":"Password fields didn't match"}
            )
        
        return data
    
    def create(self, validated_data):
        is_restaurant_admin = validated_data.pop('is_restaurant_admin')
        user = CustomUser.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            is_restaurant_admin=is_restaurant_admin
        )

        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user = user)
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)
    password = serializers.CharField(required = True, write_only = True)
    # def validate(self, data):
    #     user = authenticate(**data)
    #     print(user)
    #     if user:
    #         token = Token.objects.get(user=user)
    #         print(token)
    #         return token
    #     raise serializers.ValidationError(
    #         {"error":"Unable to log in with provided credentials"}
    #     )
    def validate(self, data):
        user = authenticate(**data)
        if user:
            # print("user"+user)
            return {'user': user}
        raise serializers.ValidationError(
            {"error": "Unable to log in with provided credentials"}
        )


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username','is_restaurant_admin']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = '__all__'