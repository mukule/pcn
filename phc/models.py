from django.db import models

# Create your models here.
class County(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Make county names unique
    
    def __str__(self):
        return self.name
    

    
class Partners(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Add more fields as needed for your partners

    def __str__(self):
        return self.name

class Subcounty(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    partners = models.ForeignKey(Partners, on_delete=models.CASCADE, null=True, blank=True)
    # Add more fields as needed

    def __str__(self):
        return self.name
