from django.db import models

class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    progress = models.FloatField(default=0.0, verbose_name="Progress (%)")

    def __str__(self):
        return self.name
    
    def get_subcounties(self):
        # Access and return the related subcounties
        return self.subcounty_set.all()
    
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
