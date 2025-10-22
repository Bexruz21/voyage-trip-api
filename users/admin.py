from django.contrib import admin
from .models import User, MembershipCard, UserMembership, Tour, BonusHistory, Region, Country, City


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "ref_id", "referrer", "balance", "is_staff")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name", "ref_id")
    ordering = ("email",)
    readonly_fields = ("ref_id",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name")}),
        ("Реферальная система", {"fields": ("ref_id", "referrer", "balance")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name", "is_staff", "is_active"),
        }),
    )


@admin.register(MembershipCard)
class MembershipCardAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "duration_months", "max_tours", "price", "popular")
    list_editable = ("popular",)
    search_fields = ("name", "code")
    list_filter = ("duration_months", "popular")

@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "card", "unique_code", "start_date", "end_date", "is_active", "used_tours")
    readonly_fields = ("unique_code", "start_date")
    list_filter = ("is_active", "card")
    search_fields = ("user__email", "unique_code")

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "display_name", "rating", "price", "best_time", "rating")
    list_filter = ("rating",)
    search_fields = ("name", "display_name", "description")


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "capital", "population", "currency", "best_time")
    list_filter = ("region", "currency")
    search_fields = ("name", "capital", "language")
    list_select_related = ("region",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "hotels", "rating", "best_time")
    list_filter = ("country__region", "country", "rating")
    search_fields = ("name", "country__name")
    list_select_related = ("country",)


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "price", "created_at")

@admin.register(BonusHistory)
class BonusHistoryAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referred_user", "amount", "created_at")