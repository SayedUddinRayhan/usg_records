from django.db import models

class ActiveManager(models.Manager):
    """Custom manager to return only active records."""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class ExamName(models.Model):
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()         # Default manager
    active = ActiveManager()           # Manager for active records only

    class Meta:
        ordering = ['name']
        verbose_name = "Exam Name"
        verbose_name_plural = "Exam Names"

    def __str__(self):
        return self.name


class ExamType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['name']
        verbose_name = "Exam Type"
        verbose_name_plural = "Exam Types"

    def __str__(self):
        return self.name


class Referrer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['name']
        verbose_name = "Referrer (Doctor)"
        verbose_name_plural = "Referrers (Doctors)"

    def __str__(self):
        return self.name


class Sonologist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ['name']
        verbose_name = "Sonologist"
        verbose_name_plural = "Sonologists"

    def __str__(self):
        return self.name
