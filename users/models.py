from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from datetime import timedelta, date, datetime
import random
import string
import uuid


def generate_ref_id():
    digits = ''.join(random.choices(string.digits, k=7))
    return f"VT-{digits}"


# ---------- USER MANAGER ----------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        if not user.ref_id:
            user.ref_id = generate_ref_id()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    

# ---------- USER ----------
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    ref_id = models.CharField(max_length=10, unique=True, default=generate_ref_id)
    referrer = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    balance = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


# ---------- MEMBERSHIP ----------
class MembershipCard(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    duration_months = models.PositiveIntegerField()
    price = models.IntegerField()
    description = models.TextField()
    features = models.JSONField(default=list, blank=True)
    popular = models.BooleanField(default=False)
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_limit = models.PositiveIntegerField(blank=True, null=True, help_text="None = без лимита")
    transfers = models.PositiveIntegerField(default=0)
    discount_tours = models.PositiveIntegerField(default=0, help_text="Количество туров со стандартной скидкой")
    discount_percent = models.PositiveIntegerField(default=0, help_text="Процент стандартной скидки")
    extra_discount_tours = models.PositiveIntegerField(default=0, help_text="Доп. количество туров со скидкой")
    extra_discount_percent = models.PositiveIntegerField(default=0, help_text="Процент доп. скидки")

    def __str__(self):
        return f"{self.name} (${self.price})"

    class Meta:
        verbose_name = "Карта членства"
        verbose_name_plural = "Карты членства"



# ---------- USER MEMBERSHIP ----------
class UserMembership(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user_memberships")
    card = models.ForeignKey(MembershipCard, on_delete=models.CASCADE, related_name="issued_cards")
    unique_code = models.CharField(max_length=20, unique=True, default="", blank=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    used_tours = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = f"VT-{uuid.uuid4().hex[:8].upper()}"
        if not self.end_date and self.card.duration_months:
            self.end_date = date.today() + timedelta(days=30 * self.card.duration_months)
        if self.end_date and self.end_date < date.today():
            self.is_active = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.card.name} ({self.unique_code})"

    class Meta:
        verbose_name = "Карта пользователя"
        verbose_name_plural = "Карты пользователей"


# ---------- REGION ----------
class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField()
    highlights = models.JSONField(default=list, blank=True)
    best_time = models.CharField(max_length=100)

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"


# ---------- COUNTRY ----------
class Country(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='countries')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    image = models.URLField()
    capital = models.CharField(max_length=100)
    population = models.CharField(max_length=50)
    language = models.CharField(max_length=100)
    currency = models.CharField(max_length=50)
    best_time = models.CharField(max_length=100)
    highlights = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


# ---------- CITY ----------
class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField()
    price = models.IntegerField(default=0, help_text="Базовая цена тура в этом городе")
    highlights = models.JSONField(default=list, blank=True)
    best_time = models.CharField(max_length=100)
    attractions = models.JSONField(default=list, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    class Meta:
        unique_together = ['country', 'name']
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return f"{self.name}, {self.country.name}"

# ---------- TOUR ----------
class Tour(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tours")
    city = models.ForeignKey("City", on_delete=models.CASCADE, related_name="tours")
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        city_price = self.city.price
        if is_new:
            membership = self.user.user_memberships.filter(is_active=True).order_by('-end_date').first()
            if membership:
                used = membership.used_tours
                discount = 0

                if used < membership.card.discount_tours:
                    discount = membership.card.discount_percent
                elif used < membership.card.discount_tours + membership.card.extra_discount_tours:
                    discount = membership.card.extra_discount_percent

                self.price = city_price * (100 - discount) / 100

                if discount > 0:
                    membership.used_tours += 1
                    membership.save()
            else:
                self.price = city_price

        super().save(*args, **kwargs)

        if is_new:
            BonusHistory.process_bonus(self.user, self)

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"


# ---------- BONUS HISTORY ----------
class BonusHistory(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bonuses_received")
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bonuses_generated")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def process_bonus(user, tour):
        # Если у пользователя нет реферера, выходим
        if not user.referrer:
            return

        referrer = user.referrer

        # Берём активную карту реферера
        ref_membership = referrer.user_memberships.filter(is_active=True).order_by('-end_date').first()
        if not ref_membership:
            return

        # Сумма бонуса берётся из карты реферера
        bonus_amount = ref_membership.card.bonus_amount
        monthly_limit = ref_membership.card.monthly_limit

        # Проверка лимита на месяц
        if monthly_limit is not None:
            current_month = datetime.now().month
            bonuses_this_month = BonusHistory.objects.filter(
                referrer=referrer,
                created_at__month=current_month
            ).count()
            if bonuses_this_month >= monthly_limit:
                return

        BonusHistory.objects.create(
            referrer=referrer,
            referred_user=user,
            tour=tour,
            amount=bonus_amount,
        )

        referrer.balance += bonus_amount
        referrer.save()


    def __str__(self):
        return f"{self.referrer.email} <- {self.referred_user.email} (${self.amount})"

    class Meta:
        verbose_name = "История бонусов"
        verbose_name_plural = "История бонусов"