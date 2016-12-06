class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name=None, last_name=None, date_of_birth=None, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=MyUserManager.normalize_email(email),
            date_of_birth=date_of_birth or timezone.now(),
            first_name=first_name or '',
            last_name=last_name or ''
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, first_name, last_name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """

        if not email:
            raise ValueError('Users must have an email address')

        if not first_name:
            raise ValueError('Users must have an first name')

        if not last_name:
            raise ValueError('Users must have an last name')

        user = self.create_user(email,
            password=password,
            date_of_birth=date_of_birth,
            first_name=first_name,
            last_name=last_name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
