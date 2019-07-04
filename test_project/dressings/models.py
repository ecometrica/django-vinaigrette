from django.db import models
import vinaigrette


class Dressing(models.Model):
    name = models.TextField(blank=True, null=True)

vinaigrette.register(Dressing, ('name',))
