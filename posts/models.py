from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='posts')
    group = models.ForeignKey('Group', models.SET_NULL, blank=True, 
                               null=True, related_name="posts")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):   
        return f"{self.pub_date} {self.author} {self.text}"   


class Group(models.Model):
    title = models.CharField(max_length=200) 
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(max_length=200)

    def __str__(self):   
        return f"{self.title}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, 
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='comments')
    text = models.TextField()
    created = models.DateTimeField('Дата комментария', auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):   
        return f"{self.created, self.author, self.post.id, self.text}"


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                             related_name='following')

    class Meta:
        unique_together = ('user', 'author')

    def __str__(self):   
        return f"{self.user, self.author}"                             