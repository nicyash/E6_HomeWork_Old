from django.db import models
from django.contrib.auth.models import User
from easy_thumbnails.fields import ThumbnailerImageField
from django.db.models.signals import post_save
from django.dispatch import receiver


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    avatar = ThumbnailerImageField(resize_source={'size': (200, 200), 'crop': 'smart'}, upload_to='', default='chat/avaDefault.jpg')
    room = models.OneToOneField(ChatRoom, on_delete=models.SET_NULL, null=True)

    def get_users(self):
        users_list = Profil.objects.filter().order_by('user')
        return list(users_list)


@receiver(post_save, sender=User)
def create_user_profil(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profil(sender, instance, **kwargs):
    instance.profil.save()


class Message(models.Model):
    author = models.ForeignKey(Profil, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    message_text = models.CharField(max_length=255)
