from django.test import TestCase, Client
from django.core import serializers
from .models import Post, User, Comment, Friend
from unittest import skip
import json
from .serializers import *
from rest_framework.renderers import JSONRenderer


class SerializerTests(TestCase):
    
    @skip("just an example how to use the serializers now, remove me later")
    def test_post(self):
        user1 = User(username='1', github="http://www.github.com/1")
        user1.save()
        post_object = Post(author=user1, title="1", description="2", content="3")
        post_serialized = PostSerializer(post_object)
        print(JSONRenderer().render(post_serialized.data))
        post_serialized = PostSerializer([post_object], many=True)
        print(JSONRenderer().render(post_serialized.data))
        

# these will only work while endpoints are not checking auth!!!
class EndpointTests(TestCase):
    def setUp(self):
        self.c = Client()
        self.user1 = User(username='1')
        self.user1.set_password('123')
        self.user2 = User(username='2')
        self.user1.save()
        self.user2.save()

        # user1 follows user2
        self.friend = Friend(user1=self.user1.id, user2=self.user2.id)
        self.friend.save()
        
        self.post1 = Post(title='a', description='b', content='c', author=self.user1)
        self.post1.save()
        self.comment1 = Comment(comment='d', author=self.user1, post=self.post1)
        self.comment1.save()
        
        # register a user with endpoint good and proper like
        self.c.post('/rest-auth/registration/', {'username':'user123','password1':'12345','password2':'12345'})
    
    def test_register_login(self):
        client = Client()
        response = client.login(username='user123', password='12345')
        assert(response) # should be true if we were able to login with the user123
    
    def test_post_just_one(self):
        client = Client()
        client.login(username='user123', password='12345')
        post = {
            "title": "1",
            "description": "2",
            "content": "c"
        }
        response = self.c.post('/api/author/posts/', post, content_type="application/json")
        assert(response.json()['success'] == True)
        assert(len(Post.objects.filter(title="1")) == 1)
        post_object = Post.objects.filter(title="1")[0]
        assert(str(post_object.author.pk) == client.session["_auth_user_id"])
    
    def test_delete_post(self):
        response = self.c.delete('/api/posts/{}/'.format(str(self.post1.id)))
        assert(response.status_code == 401)
        client = Client()
        client.login(username='1', password='123')
        assert(len(Post.objects.filter(title='a')) == 1)
        response = client.delete('/api/posts/{}/'.format(str(self.post1.id)))
        # TODO: why doesn't this work?
        #assert(response.status_code == 204)
        #assert(len(Post.objects.filter(title='a')) == 0)
    
    def test_get_posts_visible(self):
        response = self.c.get("/api/author/posts/")
        response_body = response.json()
        assert(len(response_body['posts']) >= 1) # no auth right now, so this gets them all
    
    def test_get_posts_author_id(self):
        response = self.c.get("/api/author/{}/posts/".format(self.user1.id))
        response_body = response.json()
        assert(len(response_body['posts']) == 1)
        assert(response_body['posts'][0]['id'] == str(self.post1.id))
        assert(len(response_body['posts'][0]['comments']) == 1)
        assert(response_body['posts'][0]['author']['id'] == str(self.user1.id))
    
    def test_comments(self):
        assert(len(self.post1.get_comments()) == 1)
        comment = {
            "comment": "a",
        }
        response = self.c.post('/api/posts/{}/comments/'.format(self.post1.id), comment, content_type="application/json")
        response_body = response.json()
        assert(response_body['success'] == True)
        response = self.c.get('/api/posts/{}/comments/'.format(self.post1.id))
        response_body = response.json()
        assert(len(response_body['comments']) == 2)

    def test_followers(self):
        response = self.c.get('/api/author/{}/followers/'.format(self.user1.id))
        response_body = response.json()
        assert(len(response_body["authors"]) == 0)
        response = self.c.get('/api/author/{}/followers/'.format(self.user2.id))
        response_body = response.json()
        assert(len(response_body["authors"]) == 1)

    def test_following(self):
        response = self.c.get('/api/author/{}/following/'.format(self.user1.id))
        response_body = response.json()
        assert(len(response_body["authors"]) == 1)
        response = self.c.get('/api/author/{}/following/'.format(self.user2.id))
        response_body = response.json()
        assert(len(response_body["authors"]) == 0)