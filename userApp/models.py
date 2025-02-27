from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, email, role, password=None):
        if not phone_number:
            raise ValueError("The phone number must be provided")
        if not email:
            raise ValueError("The email address must be provided")
        if not role:
            raise ValueError("The role must be provided")

        email = self.normalize_email(email)
        user = self.model(phone_number=phone_number, email=email, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, role, password=None):
        user = self.create_user(phone_number, email, role, password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20)  # Example roles: 'driver', 'admin'
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)  # Automatically set to the current date and time
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users'
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number










# def make_random_password(self, length=10):
#         """
#         Generate a random password with the specified length
#         """
#         # Define character sets for password
#         letters = string.ascii_letters
#         digits = string.digits
#         special_chars = "!@#$%^&*"
        
#         # Ensure at least one of each type
#         password = [
#             random.choice(letters.lower()),  # at least one lowercase
#             random.choice(letters.upper()),  # at least one uppercase