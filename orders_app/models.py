from django.db import models

class Cart(models.Model):
    cartId = models.BigAutoField(primary_key=True)
    userId = models.ForeignKey('user_app.CustomUser',on_delete=models.CASCADE)
    createdDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255,default='일반')

    def __str__(self):
        return f'{self.cartId} - {self.userId}'

class CartItem(models.Model):
    cartItemId = models.BigAutoField(primary_key=True)
    cartId = models.ForeignKey(Cart,on_delete=models.CASCADE)
    storeId = models.ForeignKey('restaurants_app.Restaurant',on_delete=models.CASCADE)
    menuId = models.ForeignKey('restaurants_app.Menu',on_delete=models.CASCADE)
    menuOptionId = models.ForeignKey('restaurants_app.MenuOption',on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField(default=1)
    createdDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255,default='일반')

    def __str__(self):
        return f'{self.storeId} - {self.menuId}'

class Order(models.Model):
    STATUS_CHOICES = [
        ('주문 확인','주문 확인'),
        ('조리중','조리중'),
        ('배달중','배달중'),
        ('배달 완료','배달 완료'),
        ('거절','거절'),
    ]

    orderId = models.BigAutoField(primary_key=True)
    storeId = models.ForeignKey('restaurants_app.Restaurant',on_delete=models.CASCADE, related_name='order')
    userId = models.ForeignKey('user_app.CustomUser',on_delete=models.CASCADE)

    cartId = models.ForeignKey(Cart,on_delete=models.CASCADE)

    paymentMethod = models.CharField(max_length=255)
    totalPrice = models.PositiveIntegerField()
    requestMsg = models.CharField(max_length=255,default="(없음)")
    status = models.CharField(max_length=255,choices=STATUS_CHOICES, default='주문 확인')

    createdDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)

    def has_review(self):
        return self.order_reviews.exists()

    def __str__(self):
        return f"Order ID: {self.orderId} - Store: {self.storeId} - User: {self.userId}"
    


