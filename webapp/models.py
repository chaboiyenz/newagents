from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Province(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class City(models.Model):
    province = models.ForeignKey(Province, related_name='cities', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# models.py
class Subdivision(models.Model):
    city = models.ForeignKey(City, related_name='subdivisions', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    # Image fields
    image1 = models.ImageField(upload_to='subdivisions/', blank=True, null=True)
    image2 = models.ImageField(upload_to='subdivisions/', blank=True, null=True)
    image3 = models.ImageField(upload_to='subdivisions/', blank=True, null=True)
    image4 = models.ImageField(upload_to='subdivisions/', blank=True, null=True)

    # New fields
    google_drive_link = models.URLField(max_length=255, blank=True, null=True, help_text="Optional Google Drive link")
    
    CONSTRUCTION_STATUS_CHOICES = [
        ('RFO', 'Ready For Occupancy'),
        ('Preselling', 'Preselling'),
        ('RFO/Preselling', 'RFO/Preselling'),
        ('OGC', 'On Going Construction'),
        ('RFO/Preselling/OGC', 'RFO/Preselling/OGC'),
    ]
    construction_status = models.CharField(
        max_length=20,
        choices=CONSTRUCTION_STATUS_CHOICES,
        blank=True,
        null=True
    )
    
    developer = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True, help_text="Optional location details")
    house_model = models.CharField(max_length=255, blank=True, null=True, help_text="Optional house model description")
    
    description = models.TextField(blank=True)
    commission = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Commission in %")
    price_min = models.DecimalField(max_digits=12, decimal_places=2, help_text="Minimum price in PHP")
    price_max = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maximum price in PHP")
    messenger_link = models.URLField(max_length=255, blank=True, null=True, help_text="Optional Facebook Messenger link")

    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    priority = models.CharField(
        max_length=6,
        choices=PRIORITY_CHOICES,
        default='medium',
    )

    def __str__(self):
        return self.name

    @property
    def price_range_display(self):
        return f"₱{self.price_min:,.0f} – ₱{self.price_max:,.0f}"






class Project(models.Model):
    subdivision = models.ForeignKey(Subdivision, related_name='projects', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_created = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class Memo(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='memos/', blank=True, null=True)
    description = models.TextField()
    when = models.DateTimeField()
    where = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title
    
class MemoReadStatus(models.Model):
    memo = models.ForeignKey(Memo, on_delete=models.CASCADE, related_name='read_statuses')
    employee = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming you're using the User model for employees
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.username} - {self.memo.title}"
 
    