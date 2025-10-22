from rest_framework import serializers
from .models import User, MembershipCard, UserMembership, Region, Country, City


class MembershipCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipCard
        fields = ['id', 'name', 'code', 'duration_months', 'max_tours', 'price', 'description', 'features', "popular"]


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'ref_id', 'balance', 'referrer']

class ProfileSerializer(serializers.ModelSerializer):
    user_memberships = UserMembershipSerializer(many=True, read_only=True)
    active_membership = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'first_name', 
            'last_name', 
            'ref_id', 
            'balance',
            'active_membership',
            'user_memberships'
        ]

    def get_active_membership(self, obj):
        active_membership = obj.user_memberships.filter(is_active=True).first()
        if active_membership:
            return UserMembershipSerializer(active_membership).data
        return None


# ---------- CITY SERIALIZER ----------
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            'id', 'name', 'description', 'image', 'highlights', 
            'best_time', 'attractions', 'hotels', 'rating'
        ]


# ---------- COUNTRY SERIALIZERS ----------
class CountrySerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = [
            'id', 'name', 'description', 'image', 'capital', 
            'population', 'language', 'currency', 'best_time', 
            'highlights', 'cities', 'region'
        ]


class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'description', 'image', 'capital', 'population', 'language', 'currency', 'best_time', 'highlights', 'region']


# ---------- REGION SERIALIZERS ----------
class RegionSerializer(serializers.ModelSerializer):
    countries = CountryListSerializer(many=True, read_only=True)
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = [
            'id', 'name', 'display_name', 'description', 'image',
            'countries', 'highlights', 'stats', 'price', 'best_time'
        ]

    def get_stats(self, obj):
        return {
            'rating': float(obj.rating)
        }


class RegionListSerializer(serializers.ModelSerializer):
    countries_names = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = [
            'id', 'name', 'display_name', 'description', 'image', 'highlights',
            'price', 'best_time', 'countries_names', 'rating'
        ]

    def get_countries_names(self, obj):
        return list(obj.countries.values_list('name', flat=True))