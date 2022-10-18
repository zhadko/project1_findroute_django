from django.db import models
from django.urls import reverse


class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('cities:detail', kwargs={'pk': self.pk})