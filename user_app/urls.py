from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# 다른 앱과 URL 별칭이 겹치지 않도록 app name 설정
app_name='user'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name ='register' ),
    path('login/',views.LoginView.as_view(),name = 'login'),

    # 나중에 csrf 토큰 필요시 활성화
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # csrf 토큰이 필요없는 로그아웃 실제 서비스시 사용 X GET
    # path('logout/',views.CustomLogoutView.as_view(),name='logout'),
    path('user/',views.CustomUserListView.as_view(),name='user_list'),
    
    path('one_user/',views.CurrentUserDetailView.as_view(),name='one_user'),

    path('api/address/',views.AddressListCreateView.as_view(),name='address-list-create'),
    path('api/address/<int:pk>/',views.AddressRetrieveUpdateDestroyView.as_view(),name='address-retrieve-update-destroy'),
    
    # 주소
    path('address/',views.TemplateView.as_view(template_name='address/address.html')),

    path('api/reward/',views.RewardCreateView.as_view(),name='reward-create'),
    path('api/reward/<int:pk>/',views.RewardRetrieveUpdateDestroyView.as_view(),name='reward-retrieve-update-destroy'),
]


# GET   api/address/              헤더에 들어있는 Token 값을 가지고 로그인한 유저의 전체 주소 리스트 출력
# PUT   api/address/              헤더에 있는 위치로 주소 생성
# body에 넣을값 ex) "address":"Gwangju"

# PATCH  api/address/<int:pk>/   특정 주소 수정
# DELETE api/address/<int:pk>/   특정 주소 삭제
# GET    api/address/<int:pk>/   특정 주소 가져오기