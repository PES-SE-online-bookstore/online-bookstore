from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from books import catalogue_cache
from books.models import Book


@receiver(post_save, sender=Book)
@receiver(post_delete, sender=Book)
def invalidate_catalogue_cache(sender, **kwargs):
    catalogue_cache.invalidate()
