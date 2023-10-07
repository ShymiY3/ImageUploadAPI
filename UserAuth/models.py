from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class UserTier(models.Model):
    name = models.CharField(max_length=60)
    thumbnail_sizes = models.JSONField(default=list, blank=True)
    save_original = models.BooleanField(default=False)
    generate_expiring_link = models.BooleanField(default=False)
    min_expire_seconds = models.PositiveIntegerField(default=300, null=True, blank=True)
    max_expire_seconds = models.PositiveIntegerField(default=30000, null=True, blank=True)
    
    def clean(self, *args, **kwargs):
        if not self.generate_expiring_link:
            self.min_expire_seconds = None
            self.max_expire_seconds = None
        
        if not self.save_original:
            if len(self.thumbnail_sizes) != 1:
                raise ValidationError('If save_original False, thumbnail_sizes array has to be length of 1')
        
        if not all([isinstance(x, int) for x in self.thumbnail_sizes]):
            raise (ValidationError('All values inside thumbnail_sizes array has to be integer type'))
        
        if (self.min_expire_seconds is not None) and (self.min_expire_seconds > self.max_expire_seconds):
            raise ValidationError("Min time can't be greater than max time")
        super().clean(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class User(AbstractUser):
    tier = models.ForeignKey(UserTier, on_delete=models.SET_NULL, default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding and (self.is_staff or self.is_superuser):
            self.tier = UserTier.objects.get(name="PREMIUM")
        super().save(*args, **kwargs)