from typing import Any
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
# from rest_framework.exceptions import PermissionDenied

from django.db import transaction

# from django.core.exceptions import ObjectDoesNotExist

from .models import Order, Cart, CartItem
from .serializers import OrderSerializer, CartSerializer, CartItemSerializer
from .permissions import AdminPermission, UserPermission, IsRestaurantOwnerPermission


#----------------------------------------
#웹뷰앱 형식의 코드
from django.views import View,generic
from django.shortcuts import render

class OrderTemplateView(View):
    def get(self,request):
        orders=Order.objects.all()
        context={
            'orders':orders,
        }
        return render(request,'orders/orders.html',context)

# DetailView => 특정 모델의 단일 인스턴스에 대한 세부 정보를 표시하는 뷰
# 단일 객체를 볼 수는 있지만 외래키로 연결된 객체까지 살펴보기에는 제한이 있음
# class CartView(generic.DetailView):
#     model = Cart
#     template_name = 'cart/cart.html'
#     context_object_name = 'object'

class CartView(generic.TemplateView):
    template_name='cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cartId = self.kwargs['pk']
        cart_items = CartItem.objects.filter(cartId=cartId)

        context = {
            'cart_items':cart_items,
        }

        return context


#------------------------------------------
# Order
# CreateAPIView only create : POST
# ListCreateAPIView create & list : POST & GET
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_permissions(self):
        if self.request.user.is_restaurant_admin:
            permission_class = [AdminPermission]
        else:
            permission_class = [UserPermission]
        return [permission() for permission in permission_class]
    
    def create(self,request,*args,**kwargs):
        if not request.user.is_restaurant_admin:
            token = request.headers.get('Authorization').split(' ')[1]
            try:
                authorizedToken = Token.objects.get(key=token)
                user = authorizedToken.user
                userId = user.pk
                request.data['userId']=userId
            except Token.DoesNotExist:
                return Response({"message":"Invalid token"},status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response({"message":f"An error occured:{str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message":"식당 관리자 계정으로는 주문할 수 없습니다."},status=status.HTTP_403_FORBIDDEN)
        return super().create(request,*args,**kwargs)



#=============================================================
# RetrieveUpdateDestroyAPIView : POST, PATCH, DELETE
class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.user.is_restaurant_admin:
            permission_class=[IsRestaurantOwnerPermission]
        else:
            permission_class=[UserPermission]
        return [permission() for permission in permission_class]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer=self.get_serializer(instance,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

#=============================================================
# Cart Create View
class CartCreateView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    # 리액트랑 연동하기 전이라 권한 허가 제거
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.is_restaurant_admin:
            token = request.headers.get('Authorization').split(' ')[1]
            try:
                authorizedToken = Token.objects.get(key=token)
                user = authorizedToken.user
                userId = user.pk
                request.data['userId'] = userId
            except Token.DoesNotExist:
                return Response({"message":"Invalid token"},status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response({"message":f"An error occured:{str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message":"사장님으로 로그인 하신 경우 카트를 생성할 수 없습니다."})
        return super().create(request,*args,**kwargs)
    
    # 이유를 모르겠는 동작하지 않는 코드..
    # # 요청한 사용자의 정보 저장
    # def perform_create(self, serializer):
    #     user = self.request.user
    #     print(user)
    #     try:
    #         if not user.is_restaurant_admin:
    #             # serializer.validated_data['userId'] = user.pk
    #             # serializer.save()
    #             serializer.save(userId=user)
    #         else:
    #             raise PermissionDenied("사장님으로 로그인 하신 경우 카트를 생성할 수 없습니다.")
    #     except ObjectDoesNotExist as e:
    #         return Response({"message":"로그인된 사용자가 아닙니다."},status=status.HTTP_401_UNAUTHORIZED)
    #     except Exception as e:
    #         return Response({"message":f"에러 발생: {str(e)}"},status=status.HTTP_400_BAD_REQUEST)

#=============================================================
# Cart Retrieve Destroy View
class CartRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(userId=user)
    
    def delete(self,request,*args,**kwargs):
        cart = self.get_object()
        cart.delete()
        return Response({"message":"장바구니 삭제가 완료 되었습니다."},status=status.HTTP_204_NO_CONTENT)
    

#=============================================================
# CartItem List Create View
class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CartItem.objects.filter(cartId__userId=user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            storeId = serializer.validated_data.get('storeId')
            cartId = serializer.validated_data.get('cartId').cartId
            
            user = self.request.user

            latestCart = Cart.objects.filter(pk=cartId, userId=user).first()

            with transaction.atomic():
                if latestCart:
                    cartItems = CartItem.objects.filter(cartId=latestCart.cartId)

                    if cartItems.exists():
                        existingStoreId = cartItems.first().storeId

                        if existingStoreId != storeId:
                            cartItems.delete()

                    # 여기서 cartId랑 storeId를 선언해줬었는데 뒤에 serializer에 전부 들어있었음;;
                    CartItem.objects.create(**serializer.validated_data)

            return Response({"message":"장바구니에 추가되었습니다.","data":serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        

#=============================================================
# CartItme Retrieve Update Destroy View
class CartItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    # 리액트랑 연동하기 전이라 권한 허가 제거
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer=self.get_serializer(instance,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message":"장바구니에 있던 메뉴를 삭제했습니다"},status=status.HTTP_204_NO_CONTENT)
    

#================================================
# Order의 status를 변경하는 로직
@api_view(['PUT'])
def updateOrderStatus(request,orderId):
    try:
        order = Order.objects.get(orderId=orderId)
    except Order.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    newStatus = request.data.get('newStatus')

    order.status = newStatus
    order.save()

    return Response({"message":"주문 상태 업데이트 완료"},status=status.HTTP_200_OK)

