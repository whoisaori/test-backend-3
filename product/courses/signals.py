from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from users.models import Subscription


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """
    Распределение нового студента в группу курса.

    """
    if created:
        existing_subscriptions = Subscription.objects.filter(
            product=instance.product
            )

        group_counts = existing_subscriptions.values('group').annotate(
            count=Count('id')).order_by('group')

        group_counts_dict = {group_count['group']:
                             group_count['count'] for group_count in
                             group_counts}
        min_count = min(group_counts_dict.values(), default=0)
        available_groups = [group for group, count in
                            group_counts_dict.items() if count == min_count]

        if not available_groups:
            available_groups = range(1, 11)

        instance.group = available_groups[0]
        instance.save()
