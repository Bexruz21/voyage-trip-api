from django.db import models
from rest_framework import serializers
from .models import User, MembershipCard, UserMembership, Region, Country, City, BonusHistory


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    ref_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name','ref_code']

    def create(self, validated_data):
        ref_code = validated_data.pop('ref_code', None)
        referrer = None
        if ref_code:
            referrer = User.objects.filter(ref_id=ref_code).first()
        user = User.objects.create_user(**validated_data, referrer=referrer)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'ref_id', 'balance', 'referrer']


class MembershipCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipCard
        fields = [
            'id',
            'name',
            'code',
            'duration_months',
            'max_tours',
            'price',
            'description',
            'features',
            'popular',
            'bonus_amount',
            'monthly_limit',
        ]


class UserMembershipSerializer(serializers.ModelSerializer):
    card = MembershipCardSerializer(read_only=True)

    class Meta:
        model = UserMembership
        fields = [
            "id",
            "unique_code",
            "card",
            "start_date",
            "end_date",
            "used_tours",
            "is_active",
        ]

class BonusHistorySerializer(serializers.ModelSerializer):
    tour_title = serializers.CharField(source='tour.title', read_only=True)

    class Meta:
        model = BonusHistory
        fields = ['id', 'referrer', 'referred_user', 'tour', 'tour_title', 'amount', 'created_at']


class ProfileSerializer(serializers.ModelSerializer):
    user_memberships = UserMembershipSerializer(many=True, read_only=True)
    active_membership = serializers.SerializerMethodField()
    total_referrals = serializers.SerializerMethodField()
    referral_users = serializers.SerializerMethodField()
    bonus_history = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'ref_id',
            'balance',
            'total_referrals',
            'active_membership',
            'referral_users',
            'bonus_history',
        ]

    def get_active_membership(self, obj):
        active_membership = obj.user_memberships.filter(is_active=True).first()
        if active_membership:
            return UserMembershipSerializer(active_membership).data
        return None

    def get_total_referrals(self, obj):
        return obj.referrals.count()

    def get_referral_users(self, obj):
        active_referrals = obj.referrals.filter(tours__isnull=False).distinct()
        return [
            {
                'id': u.id,
                'first_name': u.first_name,
                'last_name': u.last_name,
            } for u in active_referrals
        ]

    def get_bonus_history(self, obj):
        bonuses = BonusHistory.objects.filter(referrer=obj).order_by('-created_at')
        return BonusHistorySerializer(bonuses, many=True).data
    

# ---------- CITY SERIALIZER ----------
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            'id', 'name', 'description', 'price', 'image', 'highlights', 
            'best_time', 'attractions', 'rating'
        ]

# ---------- COUNTRY SERIALIZERS ----------
class CountrySerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True, read_only=True)
    max_rating = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = [
            'id', 'name', 'description', 'image', 'capital', 
            'population', 'language', 'currency', 'best_time', 
            'highlights', 'cities', 'region', 'max_rating', 'min_price'
        ]

    def get_max_rating(self, obj):
        return obj.cities.aggregate(models.Max('rating'))['rating__max'] or 0

    def get_min_price(self, obj):
        return obj.cities.aggregate(models.Min('price'))['price__min'] or 0


class CountryListSerializer(serializers.ModelSerializer):
    max_rating = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = [
            'id', 'name', 'description', 'image', 'capital', 'population', 
            'language', 'currency', 'best_time', 'highlights', 'region',
            'max_rating', 'min_price'
        ]

    def get_max_rating(self, obj):
        return obj.cities.aggregate(models.Max('rating'))['rating__max'] or 0

    def get_min_price(self, obj):
        return obj.cities.aggregate(models.Min('price'))['price__min'] or 0


# ---------- REGION SERIALIZERS ----------
class RegionSerializer(serializers.ModelSerializer):
    countries = CountryListSerializer(many=True, read_only=True)
    max_rating = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = [
            'id', 'name', 'display_name', 'description', 'image',
            'countries', 'highlights', 'best_time', 'max_rating', 'min_price'
        ]

    def get_max_rating(self, obj):
        return City.objects.filter(country__region=obj).aggregate(models.Max('rating'))['rating__max'] or 0

    def get_min_price(self, obj):
        return City.objects.filter(country__region=obj).aggregate(models.Min('price'))['price__min'] or 0


class RegionListSerializer(serializers.ModelSerializer):
    countries_names = serializers.SerializerMethodField()
    max_rating = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = [
            'id', 'name', 'display_name', 'description', 'image', 'highlights',
            'best_time', 'countries_names', 'max_rating', 'min_price'
        ]

    def get_countries_names(self, obj):
        return list(obj.countries.values_list('name', flat=True))

    def get_max_rating(self, obj):
        return City.objects.filter(country__region=obj).aggregate(models.Max('rating'))['rating__max'] or 0

    def get_min_price(self, obj):
        return City.objects.filter(country__region=obj).aggregate(models.Min('price'))['price__min'] or 0
