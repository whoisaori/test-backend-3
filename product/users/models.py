from django.contrib.auth.models import AbstractUser
from django.db import models
from product.models import Product


class CustomUser(AbstractUser):
    """Кастомная модель пользователя - студента."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()


class Balance(models.Model):
    """Модель баланса пользователя."""
    balance = models.DecimalField(default=1000,
                                  max_digits=10,
                                  decimal_places=2
                                  )
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'
        ordering = ('-id',)


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    group = models.IntegerField(choices=[(i, i) for i in range(1, 11)],
                                null=True,
                                blank=True
                                )

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.group = (CustomUser.objects.count() % 10) + 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
