import uuid
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_delete
from django.db import models
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from .manager import CustomUserManager
from .utils import generate_avatar_placeholder, process_uploaded_avatar


class CustomUser(AbstractUser):
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    
    first_name = models.CharField("First Name", max_length=100)
    username = models.CharField("Username", max_length=100, unique=True)
    twofa = models.BooleanField("2FA", default=False)

    avatar = models.ImageField("Profile Picture", upload_to="%Y/%m/%d/users/profile_pics/", blank=True, null=True)
    
    last_name = models.CharField("Last Name", max_length=100, blank=True, default="")
    email = models.EmailField("Email", max_length=100, blank=True, default="")
    
    phone = PhoneNumberField("Phone Number", unique=True, blank=True, null=True)
    
    bio = models.TextField("Bio", max_length=1000, blank=True, default="")
    
    date_joined = models.DateTimeField("Date Joined", auto_now_add=True)
    last_login = models.DateTimeField("Last Login", auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def clean(self):
        super().clean()
        if self.twofa and not self.email:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'email': 'Email is required if 2fa enabled.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        is_existing_user = CustomUser.objects.filter(pk=self.pk).exists()
        
        if is_existing_user:
            old_user = CustomUser.objects.get(pk=self.pk)
            
            if old_user.avatar and self.avatar != old_user.avatar:
                if old_user.avatar.storage.exists(old_user.avatar.name):
                    old_user.avatar.storage.delete(old_user.avatar.name)
                
                if self.avatar:
                    processed_file = process_uploaded_avatar(self.avatar)
                    new_name = f"{self.username}_avatar.png"
                    self.avatar.save(new_name, processed_file, save=False)

        if not self.avatar:
            file_name, file_data = generate_avatar_placeholder(self)
            self.avatar.save(file_name, file_data, save=False)
            
        elif not is_existing_user:
            processed_file = process_uploaded_avatar(self.avatar)
            new_name = f"{self.username}_avatar.png"
            self.avatar.save(new_name, processed_file, save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


@receiver(post_delete, sender=CustomUser)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    if instance.avatar:
        if instance.avatar.storage.exists(instance.avatar.name):
            instance.avatar.storage.delete(instance.avatar.name)
