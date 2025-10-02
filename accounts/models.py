#accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .accounts_manager import UserManager
from django.utils import timezone
from .utils import(generate_otp, get_otp_expiry)
from friend_system.models import Follow
from locations.models import TravelRecord


class UserAuth(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['date_joined']
        
    
    email = models.EmailField(unique=True, max_length=155)
    full_name = models.CharField(max_length=155)
    username = models.CharField(max_length=155, unique=True)
    
    profile_pic = models.ImageField(upload_to='profile_pics', default='default_profile_pic.png', null=True, blank=True, validators=[])
    profile_pic_url = models.URLField(max_length=500, null=True, blank=True)     # store remote URL
    
    phone = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    
    country = models.ForeignKey(
        "locations.Country",            #string reference to the Country model
        on_delete=models.SET_NULL,
        related_name="users_from",
        null=True,
        blank=True
    )

    
    lives_in = models.ForeignKey(
        "locations.Country",
        on_delete=models.SET_NULL,
        related_name="users_living",
        null=True,
        blank=True
    )
    
    public_profile = models.BooleanField(default=True)
    connect_contacts = models.BooleanField(default=False)
    
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expired = models.DateTimeField(blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    apple_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'    # This is the field used for authentication
    REQUIRED_FIELDS = ['username']  # required when using createsuperuser
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def get_full_name(self):
        return self.full_name
    
    def set_otp(self, otp=None, expiry_minutes=30):
        self.otp = otp or generate_otp()
        self.otp_expired = get_otp_expiry(expiry_minutes)
        
    def is_otp_valid(self, otp):
        if self.otp != otp:
            return False
        if not self.otp_expired or timezone.now() > self.otp_expired:
            self.otp = None
            self.otp_expired = None
            self.save(update_fields=["otp", "otp_expired"])
            return False
        return True
    
    
    # ---------------- Followers / Following ----------------
    @property
    def followers_count(self):
        return self.followers.filter(status='accepted').count()

    @property
    def following_count(self):
        return self.following.filter(status='accepted').count()

    def can_view_profile(self, viewer):
        """Return True if mutual follow exists."""
        return Follow.objects.filter(
            follower=self, followed=viewer, status='accepted'
        ).exists() and Follow.objects.filter(
            follower=viewer, followed=self, status='accepted'
        ).exists()

    def get_followers_queryset(self):
        return UserAuth.objects.filter(
            following__followed=self, following__status='accepted'
        )

    def get_following_queryset(self):
        return UserAuth.objects.filter(
            followers__follower=self, followers__status='accepted'
        )
        
    
    @property
    def travel_lists(self):
        travel_records = self.travel_records.select_related("country")

        visited = [rec.country.country_code for rec in travel_records if rec.visited]
        lived_in = [rec.country.country_code for rec in travel_records if rec.lived_here]
        bucket_list = [rec.country.country_code for rec in travel_records if rec.bucket_list]
        favorite = [rec.country.country_code for rec in travel_records if rec.favourite]

        # Add lives_in country if not already present
        if self.lives_in:
            code = self.lives_in.country_code
            if code not in visited:
                visited.append(code)
            if code not in lived_in:
                lived_in.append(code)

        # Add country field only to visited
        if self.country:
            code = self.country.country_code
            if code not in visited:
                visited.append(code)

        return {
            "visited_countries": visited,
            "lived_in_countries": lived_in,
            "bucket_list_countries": bucket_list,
            "favorite_countries": favorite,
        }
        
    def sync_travel_records(self):
        """Ensure user's country and lives_in are synced to TravelRecord."""
        # Sync country
        if self.country:
            rec, _ = TravelRecord.objects.get_or_create(
                user=self,
                country=self.country,
                defaults={'visited': True}
            )
            if not rec.visited:
                rec.visited = True
                rec.save(update_fields=['visited'])

        # Sync lives_in
        if self.lives_in:
            rec, _ = TravelRecord.objects.get_or_create(
                user=self,
                country=self.lives_in,
                defaults={'visited': True, 'lived_here': True}
            )
            updated = False
            if not rec.visited:
                rec.visited = True
                updated = True
            if not rec.lived_here:
                rec.lived_here = True
                updated = True
            if updated:
                rec.save(update_fields=['visited', 'lived_here'])



