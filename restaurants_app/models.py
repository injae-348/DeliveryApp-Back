from django.db import models
from django.contrib.auth import get_user_model
class Restaurant(models.Model):
    storeId = models.BigAutoField(primary_key=True)
    userId = models.ForeignKey('user_app.CustomUser',related_name='restaurant',on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    category = models.SmallIntegerField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    content = models.CharField(max_length=255,blank=True,null=True)
    minDeliveryPrice = models.IntegerField()
    deliveryTip = models.IntegerField(default=0)    
    minDeliveryTime = models.IntegerField(blank=True, null=True)
    maxDeliveryTime = models.IntegerField(blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    dibsCount = models.IntegerField(default=0)
    reviewCount = models.IntegerField(default=0)
    operationHours = models.CharField(max_length=255, blank=True, null=True)
    closedDays = models.CharField(max_length=255, blank=True, null=True)
    deliveryAddress = models.CharField(max_length=255, blank=True, null=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default="일반")

    def __str__(self):
        return f'storeId : {self.storeId} - userId : {self.userId} - name : {self.name}'

class Menu(models.Model):
    # 메뉴 ID, PK
    menuId = models.BigAutoField(primary_key=True)
    # 외래키로 가게 ID 연결
    storeId = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    content = models.CharField(max_length=100,default='상품 구성 : ')
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    menuPictureUrl = models.TextField(blank=True, null=True)
    popularity = models.BooleanField(default=False)
    createdDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default="일반")

    def __str__(self):
        return f'menuId : {self.menuId} - storeId : {self.storeId} - name : {self.name}'

class MenuImage(models.Model):
    menu = models.ForeignKey(Menu,on_delete=models.CASCADE, related_name='menu_images')
    image = models.ImageField(upload_to='menu_images/')
    createdDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default="일반")

    def __str__(self):
        return f'Image for Menu ID: {self.menu.menuId}'

class MenuOption(models.Model):
    # 메뉴 옵션 ID, PK
    menuOptionId = models.BigAutoField(primary_key=True)
    # 외래키로 메뉴 ID 연결
    menuId = models.ForeignKey(Menu, on_delete=models.CASCADE)
    # 옵션 이름
    option = models.CharField(max_length=255)
    # 옵션 내용
    content = models.CharField(max_length=255)
    # 옵션 가격
    price = models.IntegerField()
    # 생성일
    createdDate = models.DateTimeField(auto_now_add=True)
    # 수정일
    modifiedDate = models.DateTimeField(auto_now=True)
    # 상태
    status = models.CharField(max_length=255, default="활성화")

    def __str__(self):
        return f'menuOptionId: {self.menuOptionId} - menuId: {self.menuId} - option: {self.option} - content : {self.content}'
    

class Dib(models.Model):
    dibId = models.BigAutoField(primary_key=True)
    userId = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    storeId = models.ForeignKey('Restaurant',on_delete=models.CASCADE)
    createdDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255,default='일반')

    class Meta:
        unique_together = [['userId','storeId']]

    def __str__(self):
        return f"userId: {self.userId} - storeId: {self.storeId}"
    

# QR 추가
class Qrcode(models.Model):
    userId = models.ForeignKey('user_app.CustomUser', on_delete=models.CASCADE)
    orderId = models.ForeignKey('orders_app.Order', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    return_date = models.DateTimeField(auto_now_add=True, verbose_name='반납일자')
    status = models.CharField(max_length=255, default='미반납', verbose_name='상태')

    def __str__(self):
        return f'QR코드 - {self.id}'    
