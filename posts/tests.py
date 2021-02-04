from django.test import TestCase, Client
from .models import Post, Group, User, Comment, Follow
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import time


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.non_auth_user = Client()
        self.user = User.objects.create_user(username="test_user", 
                                             email="tstusr@test.ru", 
                                             password="12345")
        self.client.force_login(self.user)                                                                       
        self.group = Group.objects.create(title="test_group", slug="test_slug")
        self.client.post(reverse("new_post"),
        data={"group": "1", 'text': "New_post_test"}, follow=True)
        self.urls = [
        reverse("index"), 
        reverse("profile", kwargs={ "username": "test_user"}),
        reverse("post_view", kwargs={ "username": "test_user", "post_id": "1"}),
        reverse("group", kwargs={ "slug": "test_slug"})
        ]

    def check_post_in_page(self, url, text):
        response = self.client.get(url)
        return self.assertContains(response, text)         


    def test_profile(self):
        response = self.client.get(reverse("profile", kwargs={
                                           "username": "test_user"}))
        self.assertEqual(response.status_code, 200)

    def new_post_test(self):
        response = self.client.get(reverse("new_post"))
        self.assertEqual(response.status_code, 200)
        response = self.non_auth_user.get(reverse("new_post"), follow=True)
        self.assertRedirects(response, "/auth/login/?next=/new/", 
                             status_code=302, target_status_code=200)       

    def post_test(self):
        for url in self.urls:
            with self.subTest(url=url):
                self.check_post_in_page(url, "New_post_test")
        post = Post.objects.get(text="New_post_test")
        self.assertEqual(post.author.username, "test_user")
        quan = self.user.posts.all().count()
        self.assertEqual(quan, 1)
        self.assertEqual(post.group.id, 1)

    def post_edit_test(self): 
        for url in self.urls:
            response = self.client.get(url)
            with self.subTest(response=response):
                self.assertNotContains (response, "post_edited")       
        self.client.post(reverse("post_edit", kwargs={
                "username": "test_user", 'post_id': "1"}),
                data={"group": "1", "text": "11"}, follow=True)
        time.sleep(20)       
        for url in self.urls:
            with self.subTest(url=url):
                self.check_post_in_page(url, "11") 

    
class CrashTest(TestCase):
    def setUp(self):
        self.client = Client()
              
    def test_code_404(self):
        response = self.client.get("/test_code_404/")
        self.assertEqual(response.status_code, 404)

class ImageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", 
                                             email="tstusr@test.ru", 
                                             password="12345")
        self.client.force_login(self.user)                                                                       
        self.group = Group.objects.create(title="test_group", slug="test_slug")
        small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
        )
        self.img = SimpleUploadedFile('small.gif', small_gif, 
                                      content_type='image/gif')
        self.img_post = self.client.post(reverse("new_post"),
        data={"group": "1", 'text': "post_with_image_test", "image": self.img},
        follow=True) 
        self.urls = [
        reverse("index"),
        reverse("profile", kwargs={ "username": "test_user"}),
        reverse("post_view", kwargs={ "username": "test_user", "post_id": "1"}),
        reverse("group", kwargs={ "slug": "test_slug"})
        ]

    def image_test(self):
        for url in self.urls:
            response = self.client.get(url)
            with self.subTest(response=response):
                self.assertContains(response, "<img class=")
                self.assertContains(response, "post_with_image_test") 

    def not_image_test(self):
        small_gif = (b"no_photo")
        self.img = SimpleUploadedFile('small.gif', small_gif, 
                                      content_type='image/gif')
        response = self.client.post(reverse("new_post"),
        data={
              "group": "1", 'text': "post_with_not_image_test", 
              "image": self.img
        }, follow=True)
        self.assertFormError(response, "form", "image", 
            "Загрузите правильное изображение. Файл, ко"\
            "торый вы загрузили, поврежден или не является изображением.")


class CacheTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", 
                                             email="tstusr@test.ru", 
                                             password="12345")

    def test_cache(self):
        self.client.get(reverse("index"))                                        
        Post.objects.create(text="cache_test", author=self.user) 
        response = self.client.get(reverse("index"))
        self.assertNotContains(response, "cache_test")


class FollowAndCommentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.fol_user_client = Client()
        self.user = User.objects.create_user(username="test_user", 
                                             email="tstusr@test.ru", 
                                             password="12345")
        self.fol_user = User.objects.create_user(username="folowing_user", 
                                             email="follow@test.ru", 
                                             password="12345") 
        self.not_fol_user = User.objects.create_user(username="not_folowing_user", 
                                             email="follow@test.ru", 
                                             password="12345")  
        Post.objects.create(text="Follow_index_test", author=self.fol_user)  
        Post.objects.create(text="Not_Follow_index_test", 
                            author=self.not_fol_user)                                                                                                                  
        self.client.force_login(self.user) 
        self.client.post(reverse("profile_follow", kwargs={
                                    "username": self.fol_user.username}), 
                                    follow=True)         

    def follow_test(self):
        result = Follow.objects.filter(user=self.user, 
                                         author=self.fol_user).exists() 
        self.assertTrue(result)

    def unfollow_test(self):    
        self.client.post(reverse("profile_unfollow", kwargs={
                                    "username": self.fol_user.username}), 
                                    follow=True) 
        result = Follow.objects.filter(user=self.user, 
                                         author=self.fol_user).exists() 
        self.assertFalse(result)  

    def follow_index_test(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Follow_index_test")         
        self.assertContains(response, "Not_Follow_index_test")
        response = self.client.get(reverse("follow_index"))
        self.assertContains(response, "Follow_index_test")         
        self.assertNotContains(response, "Not_Follow_index_test")

    def comment_test(self):
        response = self.client.post(reverse("add_comment", kwargs={
                "username": "folowing_user", "post_id": "1"}),
                data={'text': "test_comment"}, follow=True)
        self.assertRedirects(response, "/folowing_user/1/", 
                             status_code=302, target_status_code=200) 
        response = self.client.get(reverse("post_view", kwargs={
                                           "username": "folowing_user", 
                                           "post_id": "1"}))  
        self.assertContains(response, "test_comment")                                                
        response = self.fol_user_client.post(reverse("add_comment", kwargs={
                'username': "folowing_user", "post_id": "1"}),
                data={"text": "test_comment"}, follow=True)
        self.assertRedirects(response, 
                             "/auth/login/?next=/folowing_user/1/comment/", 
                             status_code=302, target_status_code=200)
                                                            

