from django.db import models

from django.db import models

class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    progress = models.FloatField(default=0.0, verbose_name="Progress (%)")
    
    # Fields to track subcounty counts by status
    not_started = models.PositiveIntegerField(default=0)
    in_progress = models.PositiveIntegerField(default=0)
    fully_established = models.PositiveIntegerField(default=0)
    partner_support = models.PositiveIntegerField(default=0)
    
    # New status field with a default value of 0
    status = models.PositiveIntegerField(default=0)
    styleid = models.CharField(max_length=10, unique=True, null=True)
    
    def __str__(self):
        return self.name


    
class Partners(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Subcounty(models.Model):
    STATUS_CHOICES = (
        (0, 'Not Started'),
        (1, 'In Progress'),
        (2, 'Fully Established'),
    )

    county = models.ForeignKey(County, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    partners = models.ManyToManyField(Partners, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    def __str__(self):
        return self.name
