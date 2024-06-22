from rest_framework import status,generics,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .permissions import IsRestaurantAdminOrReadOnly, CustomListRetrievePermission, IsOwnerOrReadOnly, IsOwnerOrReadOnlyOption

from .models import Restaurant, Menu, MenuOption, Dib, MenuImage, Qrcode
from .serializers import RestaurantSerializer, MenuSerializer, MenuOptionSerializer, DibSerializer, MenuImageSerializer, QrcodeSerializer

from django.utils import timezone
import logging

# 웹뷰웹 형식의 HTML 파일을 리턴할 코드
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse

# from orders_app.utils import cart_has_items

# TemplateView => 특정 템플릿 파일을 렌더링 하기 위한 뷰
class RestaurantListView(TemplateView):
    template_name = 'restaurants/restaurants_list.html'  # 템플릿 파일의 경로를 지정해야 합니다.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurants = Restaurant.objects.all()
        context['restaurants'] = restaurants
        return context

class RestaurantDetailView(TemplateView):
    template_name = 'restaurants/restaurants_detail.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        # user = self.request.user
        restaurant_id = kwargs['pk']
        restaurant = get_object_or_404(Restaurant,pk=restaurant_id)
        menu_categories = Menu.objects.filter(storeId=restaurant_id).values_list('category',flat=True).distinct()
        categorized_menus = {}

        for category in menu_categories:
            categorized_menus[category]=Menu.objects.filter(storeId=restaurant_id,category=category)

        # cart_item_exist = cart_has_items(user)

        context = {
            'restaurant':restaurant,
            'menu_categories':menu_categories,
            'categorized_menus':categorized_menus,
            # 'cart_item_exist':cart_item_exist,

        }
        return context




# Authentication - 사용자의 신원(회원/비회원/관리자 등을 확인)을 확인하는 절차
# Permission - 특정 서비스를 어느 정도로 이용할 수 있는지에 대한 권한

# ============================================================
# Restaurant ViewSet
class RestaurantViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsRestaurantAdminOrReadOnly]
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer    

    #POST
    def create(self,request):
        # 현재 로그인한 사용자 정보 가져와서 userId 칸 추가
        current_user = request.user
        request.data['userId'] = current_user.id
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # GET
    def list(self,request):
        queryset = self.queryset
        serializer = self.serializer_class(queryset,many=True)
        return Response(serializer.data)
    
    # GET
    def retrieve(self,request,pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Restaurant.DoesNotExist:
            return Response({'message':'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

    # PUT
    def update(self,request,pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset,data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Restaurant.DoesNotExist:
            return Response({'message':'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

    # DELETE
    def destroy(self, request, pk=None):
            try:
                queryset = self.queryset.get(pk=pk)
                queryset.delete()
                return Response({'message': 'Restaurant deleted'})
            except Restaurant.DoesNotExist:
                return Response({'message': 'Restaurant not found'}, status=status.HTTP_404_NOT_FOUND)

    # permmision action 별로 권한 설정     
    def get_permissions(self):
        if self.action in ['list','retrieve']:
            permission_classes = [CustomListRetrievePermission]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]


# ============================================================
# MENU VIEWSET
class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer
    queryset = Menu.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    # 해당 레스토랑의 메뉴만 가져오기
    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        queryset = Menu.objects.filter(storeId=restaurant_id)
        return queryset
    
    # POST
    def create(self, request, *args, **kwargs):
        # url에서 restaurant id 가져옴
        store_id = self.kwargs.get('restaurant_id')
        
        # 현재 로그인한 사용자의 가게를 가져옴
        user = self.request.user
        user_restaurants = user.restaurant.all()

        try:
            user_restaurant = user_restaurants.get(storeId = store_id)
        except user_restaurants.model.DoesNotExist:
            return Response({"message":"Requested store not found for this user"}, status=status.HTTP_400_BAD_REQUEST)

        request.data['storeId'] = user_restaurant.pk

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # PUT
    def update(self,request,*args, **kwargs):
        store_id = self.kwargs.get('restaurant_id')

        user = self.request.user
        user_restaurants = user.restaurant.all()

        try:
            user_restaurant = user_restaurants.get(storeId=store_id)
        except user_restaurants.model.DoesNotExist:
            return Response({"message":"Requested store not found for this user"}, status=status.HTTP_400_BAD_REQUEST)

        request.data['storeId'] = user_restaurant.pk

        instance = self.get_object()
        serializer = self.get_serializer(instance,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
    # PATCH
    def partial_update(self, request, *args, **kwargs):
        store_id = self.kwargs.get('restaurant_id')

        user = self.request.user
        user_restaurants = user.restaurant.all()

        try:
            user_restaurant = user_restaurants.get(storeId=store_id)
        except user_restaurants.model.DoesNotExist:
            return Response({"message": "Requested store not found for this user"}, status=status.HTTP_400_BAD_REQUEST)

        request.data['storeId'] = user_restaurant.pk

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)  # partial=True로 설정하여 일부 필드만 변경 가능하도록 함
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
    # DELETE
    def destroy(self, request, *args, **kwargs):
        restaurant_id = self.kwargs.get('restaurant_id')  # URL에서 레스토랑 ID 가져옴

        user = self.request.user
        user_restaurants = user.restaurant.all()

        try:
            user_restaurant = user_restaurants.get(storeId=restaurant_id)
        except user_restaurants.model.DoesNotExist:
            return Response({"message": "Requested store not found for this user"}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        instance.delete()

        return Response({"message": "Object deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# ============================================================
# MenuImg ViewSet
class MenuImageViewSet(viewsets.ModelViewSet):
    serializer_class = MenuImageSerializer
    queryset = MenuImage.objects.all()
    permission_classes = [IsOwnerOrReadOnly]  # 권한 설정에 따라 변경

    # 해당 메뉴의 이미지들만 가져오기
    def get_queryset(self):
        menu_id = self.kwargs.get('menu_id')
        queryset = MenuImage.objects.filter(menu_id=menu_id)
        return queryset

    # 이미지 업로드
    def create(self, request, *args, **kwargs):
        menu_id = self.kwargs.get('menu_id')  # URL에서 메뉴 ID 가져옴

        # request.data에 메뉴 ID 추가
        request.data['menu'] = menu_id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 이미지 수정
    def update(self, request, *args, **kwargs):
        menu_id = self.kwargs.get('menu_id')  # URL에서 메뉴 ID 가져옴

        # request.data에 메뉴 ID 추가
        request.data['menu'] = menu_id

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    # 이미지 삭제
    def destroy(self, request, *args, **kwargs):
        menu_image = self.get_object()
        menu_image.delete()
        return Response({"message":"이미지가 정상적으로 지워졌습니다."},status=status.HTTP_204_NO_CONTENT)
    
# ============================================================
# MenuOption ViewSet
class MenuOptionViewSet(viewsets.ModelViewSet):
    serializer_class = MenuOptionSerializer
    permission_classes = [IsOwnerOrReadOnlyOption]

    def get_queryset(self):
        menu_id = self.kwargs.get('menu_id')
        return MenuOption.objects.filter(menuId=menu_id)
    

    def create(self,request,*args,**kwargs):
        menu_id = kwargs.get('menu_id')

        # 해당 메뉴 ID가 존재하는지 확인
        try:
            menu = Menu.objects.get(menuId=menu_id)
        except Menu.DoesNotExist:
            return Response({"message":"Menu not found"},status=status.HTTP_400_BAD_REQUEST)
        
        # 현재 로그인한 사용자의 소유 여부 확인
        if menu.storeId.userId != request.user:
            return Response({"message":"Permission denied"},status=status.HTTP_403_FORBIDDEN)
        
        request.data['menuId'] = menu_id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self,request,*args,**kwargs):
        menu_id = kwargs.get('menu_id')
        menu_option_id = kwargs.get('pk')

        try:
            menu_option = MenuOption.objects.get(pk=menu_option_id,menuId=menu_id)
            menu = menu_option.menuId
        except MenuOption.DoesNotExist:
            return Response({"message":"Menu Option not found"},status=status.HTTP_400_BAD_REQUEST)

        menu = menu_option.menuId

        # 현재 로그인한 사용자 소유 여부 확인
        if menu.storeId.userId != request.user:
            return Response({"message":"Permission denied"},status=status.HTTP_403_FORBIDDEN)
        
        request.data['menuId'] = menu_id
        request.data['menuOptionId'] = menu_option_id

        serializer = self.get_serializer(instance=menu_option,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        menu_id = kwargs.get('menu_id')
        menu_option_id = kwargs.get('pk')

        try:
            menu_option = MenuOption.objects.get(pk=menu_option_id,menuId=menu_id)
            menu = menu_option.menuId
        except MenuOption.DoesNotExist:
            return Response({"message":"Menu Option not found"},status=status.HTTP_400_BAD_REQUEST)

        if menu.storeId.userId != request.user:
            return Response({"message":"Permission denied"},status=status.HTTP_403_FORBIDDEN)
         
        menu_option.delete()

        return Response({"message":"Menu Option deleted successfully"},status=status.HTTP_204_NO_CONTENT)


# ============================================================
# DibViewSet
class DibViewSet(viewsets.ModelViewSet):
    queryset = Dib.objects.all()
    serializer_class = DibSerializer
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def create(self,request, *args,**kwargs):
        storeId = request.data.get('storeId')
        existing_dib = Dib.objects.filter(userId=request.user, storeId=storeId).first()

        if existing_dib:
            if existing_dib.status=='활성화':
                existing_dib.status = '일반'
                existing_dib.save()
                serializer = DibSerializer(existing_dib)
                return Response({"data":serializer.data,"message":"좋아요를 누릅니다."},status=status.HTTP_200_OK)
            else:
                existing_dib.status = '활성화'
                existing_dib.save()
                serializer = DibSerializer(existing_dib)
                return Response({"data":serializer.data,"message":"좋아요를 취소합니다."},status=status.HTTP_400_BAD_REQUEST)
        else:
            data = request.data.copy()
            data['userId'] = request.user.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    @action(detail=False,methods=['get'], authentication_classes=[],permission_classes=[])
    def get_likes_count(self,request,*args,**kwargs):
        storeId = request.query_params.get('storeId')
        active_likes_count = Dib.objects.filter(storeId=storeId,status='활성화').count()
        return Response({'좋아요한 수 ':active_likes_count})

# ============================================================
# Qrcode

class QrcodeAPIView(APIView):
    """
    POST 요청을 받으면 Qrcode 데이터베이스에 저장하고 GET 요청을 받으면 내용을 조회합니다.
    """
    def post(self, request, format=None):
        serializer = QrcodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        queryset = Qrcode.objects.all()
        serializer = QrcodeSerializer(queryset, many=True)
        return Response(serializer.data)


# 반납 QR코드

logger = logging.getLogger(__name__)

class VerifyQrcodeAPIView(APIView):
    def post(self, request, format=None):
        user_id = request.data.get('userId')
        order_id = request.data.get('orderId')

        if not user_id or not order_id:
            return Response({"error": "userId and orderId are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            qrcode = Qrcode.objects.filter(userId=user_id, orderId=order_id).first()
            if not qrcode:
                return Response({"error": "QR code not found."}, status=status.HTTP_404_NOT_FOUND)

            qrcode.return_date = timezone.now()
            qrcode.status = '반납'
            qrcode.save()

            return Response({"message": "QR code verified and return date updated."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# # CreateAPIView 사용
# class dibCreateView(generics.CreateAPIView):
#     serializer_class = DibSerializer

#     authentication_classes=[TokenAuthentication]
#     # permission_classes=[]

#     def create(self,request, *args,**kwargs):
#         storeId = request.data.get('storeId')
#         existing_dib = Dib.objects.filter(userId=request.user, storeId=storeId).first()

#         if existing_dib:
#             if existing_dib.status=='활성화':
#                 existing_dib.status = '일반'
#                 existing_dib.save()
#                 serializer = DibSerializer(existing_dib)
#                 return Response({"data":serializer.data,"message":"좋아요를 누릅니다."},status=status.HTTP_200_OK)
#             else:
#                 existing_dib.status = '활성화'
#                 existing_dib.save()
#                 serializer = DibSerializer(existing_dib)
#                 return Response({"data":serializer.data,"message":"좋아요를 취소합니다."},status=status.HTTP_400_BAD_REQUEST)
#         else:
#             data = request.data.copy()
#             data['userId'] = request.user.id
#             serializer = self.get_serializer(data=data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data,status=status.HTTP_201_CREATED)

'''
# Restaurant CRUD
class RestaurantCreateView(APIView):
    permission_classes = [IsRestaurantAdminOrReadOnly]

    def post(self,request,format=None):
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class RestaurantRetrieveView(generics.RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class RestaurantUpdateView(generics.UpdateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class RestaurantDestroyView(generics.DestroyAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


# Menu CRUD
class MenuCreateView(generics.CreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class MenuListView(generics.ListAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class MenuListByStoreIdView(generics.ListAPIView):
    serializer_class = MenuSerializer

    def get_queryset(self):
        store_id = self.kwargs['storeId']
        queryset = Menu.objects.filter(storeId=store_id)
        return queryset
    
class MenuRetrieveView(generics.RetrieveAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class MenuUpdateView(generics.UpdateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class MenuDestroyView(generics.DestroyAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer    

    
# MenuOption CRUD
class MenuOptionCreateView(generics.CreateAPIView):
    queryset = MenuOption.objects.all()
    serializer_class = MenuOptionSerializer

class MenuOptionListByMenuIdView(generics.ListAPIView):
    serializer_class = MenuOptionSerializer

    def get_queryset(self):
        menu_id = self.kwargs['menuId']
        queryset = MenuOption.objects.filter(menuId=menu_id)
        return queryset

class MenuOptionRetrieveView(generics.RetrieveAPIView):
    queryset = MenuOption.objects.all()
    serializer_class = MenuOptionSerializer

class MenuOptionUpdateView(generics.UpdateAPIView):
    queryset = MenuOption.objects.all()
    serializer_class = MenuOptionSerializer

class MenuOptionDestroyView(generics.DestroyAPIView):
    queryset = MenuOption.objects.all()
    serializer_class = MenuOptionSerializer

'''