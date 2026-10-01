from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, first_name, username, password=None, **extra_fields):
        if not first_name:
            raise ValueError("First Name is missing.")
        if not username:
            raise ValueError("Username is missing.")

        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)

        twofa = extra_fields.pop("twofa", False)

        if not password:
            password = self.make_random_password()

        user = self.model(
            first_name=first_name,
            username=username,
            twofa=twofa,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        extra_fields.setdefault('twofa', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(first_name, username, password, **extra_fields)
