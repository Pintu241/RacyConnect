from django.db import models
from django.utils.text import slugify

class ScrapCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(help_text="Detailed description of scrap items accepted under this category")
    icon = models.CharField(max_length=50, default='bi-recycle', help_text="Bootstrap icon class name, e.g. bi-newspaper")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    base_rate_per_kg = models.DecimalField(max_digits=8, decimal_places=2, help_text="Current indicative market rate per kg")
    min_rate_per_kg = models.DecimalField(max_digits=8, decimal_places=2, help_text="Minimum indicative rate per kg")
    max_rate_per_kg = models.DecimalField(max_digits=8, decimal_places=2, help_text="Maximum indicative rate per kg")
    unit = models.CharField(max_length=20, default='kg')
    recyclability_impact = models.CharField(max_length=255, default='Reduces landfill waste & greenhouse gas emissions')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Scrap Category"
        verbose_name_plural = "Scrap Categories"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (₹{self.base_rate_per_kg}/{self.unit})"
