from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import RegisterSerializer, UserSerializer, MembershipCardSerializer, ProfileSerializer, RegionListSerializer, RegionSerializer, CountryListSerializer, CountrySerializer, CitySerializer
from .models import MembershipCard, Region, Country, City
from .management.commands import deactivate_expired_cards


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # deactivate_expired_cards()
        return self.request.user

class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # deactivate_expired_cards()  # раскомментируйте если нужно
        return self.request.user

class MembershipCardListView(generics.ListAPIView):
    queryset = MembershipCard.objects.all()
    serializer_class = MembershipCardSerializer
    permission_classes = [permissions.AllowAny] 

# ---------- REGION VIEWS ----------
class RegionListView(generics.ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionListSerializer
    permission_classes = [permissions.AllowAny]


class RegionDetailView(generics.RetrieveAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [permissions.AllowAny]


# ---------- COUNTRY VIEWS ----------
class CountryListView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountryListSerializer
    permission_classes = [permissions.AllowAny]


class CountryDetailView(generics.RetrieveAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]


# ---------- CITY VIEWS ----------
class CityListView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]


class CityDetailView(generics.RetrieveAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]


class RegionCountriesView(generics.ListAPIView):
    serializer_class = CountryListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        region_id = self.kwargs['region_id']
        return Country.objects.filter(region_id=region_id)


class CountryCitiesView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        country_id = self.kwargs['country_id']
        return City.objects.filter(country_id=country_id)