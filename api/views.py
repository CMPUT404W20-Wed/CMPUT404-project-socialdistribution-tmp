from django.core import serializers
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import JSONRenderer
from .serializers import PostSerializer, CommentSerializer, UserSerializer
from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User, Post, Comment, Friend, LocalLogin, RemoteLogin, url
from django.core.paginator import Paginator
from .utils import *
from .filters import apply_filter
import json
import requests
import time
from django.db.models import Q

request_last_updated = 0

from .views_.media import *
from .views_.login import *

# TODO: serializers should only spit out certain fields (per example-article.json), ez but tedious

# index
# We may want to change this to a redirect or something along those lines in future
# just making this for now to have an index function
def index(request):
    method = request.method
    if method == "POST":
        users = User.objects.values_list('id')
        return redirect("/posts/")
    else:
        return HttpResponse(status=405, content="Method Not Allowed")

# author/posts
def posts_visible(request):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    ensure_data()
    method = request.method
    if method == "GET":
        page, size, filter_ = get_post_query_params(request)
        # TODO: posts visible to the currently authenticated user
        posts = apply_filter(request, filter_)
        posts_pages = Paginator(posts, size)
        response_body = {
            "query": "posts",
            "count": len(posts),
            "size": size,
            "posts": PostSerializer(posts_pages.page(page), many=True).data
        }
        response_body.update(create_pagination_info(request, posts_pages, page, size, filter_))
        return HttpResponse(content=JSONRenderer().render(response_body), status=200, content_type="application/json")
    if method == "POST":
        post = json.loads(request.body)
        post["author"] = request.user
        post = Post.objects.create(**post)
        response_body = JSONRenderer().render({
            "query": "posts",
            "success": True,
            "message": "Post Created",
            "post": PostSerializer(post).data
        })
        return HttpResponse(content=response_body, status=200, content_type="application/json")
    return HttpResponse(status=405, content="Method Not Allowed")

# posts by author id
# author/<uuid:aid>/posts
def posts_by_aid(request, aid):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    ensure_data()
    method = request.method
    if method == "GET":
        page, size, filter_ = get_post_query_params(request)
        # all posts made by author id aid visible to currently authed user
        # TODO: this thing here ignores the visibility thing
        user = User.objects.get(pk=aid)
        posts = Post.objects.filter(author=user)
        posts_pages = Paginator(posts, size)
        response_body = {
            "query": "posts",
            "count": len(posts),
            "size": size,
            "posts": PostSerializer(posts_pages.page(page), many=True).data
        }
        response_body.update(create_pagination_info(request, posts_pages, page, size, filter_))
        return HttpResponse(content=JSONRenderer().render(response_body), content_type="application/json", status=200)
    else:
        return HttpResponse(status=405, content="Method Not Allowed")

# posts/
def all_posts(request):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    method = request.method
    # grab_external_data()
    ensure_data()
    if method == "GET":
        page, size, filter_ = get_post_query_params(request)
        posts = apply_filter(request, filter_)
        posts_pages = Paginator(posts, size)
        response_body = {
            "query": "posts",
            "count": len(posts),
            "size": size,
            "posts": PostSerializer(posts_pages.page(page), many=True).data
        }
        response_body.update(create_pagination_info(request, posts_pages, page, size, filter_))
        return HttpResponse(content=JSONRenderer().render(response_body), content_type="application/json", status=200)
    else:
        return HttpResponse(status=405, content="Method Not Allowed")

# posts by post id
# posts/<uuid:pid>
def posts_by_pid(request, pid):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    ensure_data()
    method = request.method
    if method == "GET":
        post = Post.objects.get(pk=pid)
        response_body = JSONRenderer().render({
            "query": "getPost",
            "post": PostSerializer(post).data
        })
        return HttpResponse(content=response_body, content_type="application/json", status=200)
    elif method == "DELETE":
        post = Post.objects.get(pk=pid)
        if post.author.id == request.user.pk:
            post.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)
    elif method == "PUT":
        post = Post.objects.get(pk=pid)
        if post.author.id == request.user.pk:
            post.__dict__.update(**json.loads(request.body))
            post.save()
            response_body = JSONRenderer().render({
                "query": "putPost",
                "post": PostSerializer(post).data
            })
            return HttpResponse(content=response_body, content_type="application/json", status=200)
        else:
            return HttpResponse(status=401)
    return HttpResponse(status=405, content="Method Not Allowed")

# comments by post id
# posts/<uuid:pid>/comments
def comments_by_pid(request, pid):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    ensure_data()
    method = request.method
    if method == "GET":
        page, size, filter_ = get_post_query_params(request)
        post = Post.objects.get(pk=pid)
        comments = Comment.objects.filter(post=post)
        comments_pages = Paginator(comments, size)
        response_body = {
            "query": "comments",
            "count": len(comments),
            "size": size,
            "comments": CommentSerializer(comments_pages.page(page), many=True).data
        }
        response_body.update(create_pagination_info(request, comments_pages, page, size, filter_))
        return HttpResponse(content=JSONRenderer().render(response_body), content_type="application/json", status=200)
    elif method == "POST":
        comment = json.loads(request.body)
        comment["author"] = request.user
        comment["post"] = Post.objects.get(pk=pid)
        comment = Comment.objects.create(**comment)
        response_body = JSONRenderer().render({
            "query": "addComment",
            "success": True,
            "message": "Comment Added",
            "comment": CommentSerializer(comment).data
        })
        return HttpResponse(content=response_body, content_type="application/json", status=200)
    return HttpResponse(status=405, content="Method Not Allowed")

# TODO: pid not actually needed, but we can check cid is a comment of pid if we want
def comments_by_cid(request, pid, cid):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    ensure_data()
    method = request.method
    comment = Comment.objects.get(pk=cid)
    if comment.author.id == request.user.pk:
        if method == "DELETE":
            comment.delete()
            return HttpResponse(status=204)
        elif method == "PUT":
            comment.__dict__.update(**json.loads(request.body))
            comment.save()
            response_body = JSONRenderer().render({
                "query": "putComment",
                "comment": CommentSerializer(comment).data
            })
            return HttpResponse(content=response_body, content_type="application/json", status=200)
        else:
            return HttpResponse(status=405, content="Method Not Allowed")
    else:
        return HttpResponse(stauts=401)


# Query for FOAF
# author/<uuid:aid>/friends/
def friends_by_aid(request, aid):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    method = request.method
    # Get the friends of the author
    if method == "GET":
        #
        friends = Friend.objects.filter(user1=aid)
        friend_list = []
        for f in friends:
            friend_profile = User.objects.get(id=f.user2)
            twoWayFriendship = Friend.objects.filter(user1=f.user2, user2=aid)
            if twoWayFriendship:
                # Put each friend in json format
                friend_list.append(friend_profile.host+'/author/'+str(friend_profile.id))
                
        response_body = JSONRenderer().render({
            "query": "friends",
            "authors": friend_list,
            "count": len(friend_list)
        })
        return HttpResponse(content=response_body, content_type="application/json", status=200)
    # Check if anyone in the list is friends with the author
    if method == "POST":
        body = json.loads(request.body)
        # List of authors we are checking against
        author_list = body["authors"]
        author_profile = User.objects.get(id=aid)
        friend_list = []
        for a in author_list:
            # friend_profile = User.objects.get(id=a.split('/')[-1])
            friendship = Friend.objects.filter(user1=aid, user2=a.split('/')[-1]) and Friend.objects.filter(user2=aid, user1=a.split('/')[-1])
            if friendship:
                friend_list.append(a)
        response_body = JSONRenderer().render({
            "query": "friends",
            "author": author_profile.host+"/author/"+str(aid),
            "authors": friend_list
        })
        return HttpResponse(content=response_body, content_type="application/json", status=200)
    else:
        return HttpResponse(status=405, content="Method Not Allowed")

# author/<authorid>/friends/<authorid2>/
def friendship_by_aid(request, aid1, aid2):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    method = request.method
    if method == "GET":
        friendship = Friend.objects.filter(user1=aid1, user2=aid2) and Friend.objects.filter(user2=aid1, user1=aid2)
        if not friendship:
            # TODO: Return the author list with the stripped protocol
            user1_profile = User.objects.get(id=aid1)
            user2_profile = User.objects.get(id=aid2)
            response_body = JSONRenderer().render({
                "query": "friends",
                "friends": "false",
                "authors": [
                    user1_profile.host+"/author/"+str(aid1),
                    user2_profile.host+"/author/"+str(aid2)
                ]
            })
        else:
            # TODO: Return the author list with the stripped protocol
            user1_profile = User.objects.get(id=aid1)
            user2_profile = User.objects.get(id=aid2)
            response_body = JSONRenderer().render({
                "query": "friends",
                "friends":"true",
                "authors": [
                    user1_profile.host+"/author/"+str(aid1),
                    user2_profile.host+"/author/"+str(aid2)
                ]
            })
        return HttpResponse(content=response_body, content_type="application/json", status=200)
    if method == "DELETE":
        if aid1 == request.user.pk:
            Friend.objects.get(user1=aid1, user2=aid2).delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=401, content="Unauthorized")
            
    else:
        return HttpResponse(status=405, content="Method Not Allowed")

# friendrequest/
def friendrequest(request):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    method = request.method
    if method == "POST":
        body = json.loads(request.body)
        if body["query"] == "friendrequest":
            requester_id = body["author"]["id"].split('/')[-1]
            requestee_id = body["friend"]["id"].split('/')[-1]
            request = {
                "user1": requester_id,
                "user2": requestee_id,
            }
            Friend.objects.create(**request)
            return HttpResponse(status=200)

        else:
            return HttpResponse(status=400, content="Bad Request")
    else:
        return HttpResponse(status=405, content="Method Not Allowed")

# author/<authorid>/followers/
def followers(request, aid):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    method = request.method
    if method == "GET":
        followers = Friend.objects.filter(user2=aid)
        
        follower_list = []
        for f in followers:
            friend = Friend.objects.filter(user1=aid, user2=f.user1) and Friend.objects.filter(user2=aid, user1=f.user1)
            if not friend:
                follower_list.append(f.user1)

        response_body = JSONRenderer().render({
            "query": "followers",
            "authors": follower_list,
            "count": len(follower_list)
        })
        return HttpResponse(content=response_body, content_type="application/json", status=200)
    else:
        return HttpResponse(status=405, content="Method Not Allowed")

# author/<authorid>/following/
def following(request, aid):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    method = request.method
    if method == "GET":
        following = Friend.objects.filter(user1=aid)

        following_list = []
        for f in following:
            friend = Friend.objects.filter(user1=aid, user2=f.user2) and Friend.objects.filter(user2=aid, user1=f.user2)
            if not friend:
                following_list.append(f.user2)

        response_body = JSONRenderer().render({
            "query": "following",
            "authors": following_list,
            "count": len(following_list),
        })
        return HttpResponse(content=response_body, content_type="application/json", status=200)
    else:
        return HttpResponse(status=405, content="Method Not Allowed")

# Returns a specified profile
# author/<uuid:aid>/
def profile(request, aid):
    if not (request.user.is_authenticated or authenticate_node(request)):
        return HttpResponse(status=401, content="Unauthorized")
    ensure_data()
    method = request.method
    if method == "GET":
        friends = Friend.objects.filter(user1=aid)
        friend_list = []
        for f in friends:
            friend_profile = User.objects.get(id=f.user2)
            twoWayFriendship = Friend.objects.filter(user1=f.user2, user2=aid)
            if twoWayFriendship:
                # Put each friend in json format
                friend_list.append({
                    "id": friend_profile.host+'/author/'+str(friend_profile.id),
                    "host": friend_profile.host,
                    "displayName": friend_profile.username,
                    "url": friend_profile.host+'/author/'+str(friend_profile.id),
                })

        following = Friend.objects.filter(user1=aid)
        following_list = []
        for f in following:
            friend = Friend.objects.filter(user1=aid, user2=f.user2) and Friend.objects.filter(user2=aid, user1=f.user2)
            if not friend:
                following_list.append(f.user2)

        followers = Friend.objects.filter(user2=aid)
        follower_list = []
        for f in followers:
            friend = Friend.objects.filter(user1=aid, user2=f.user1) and Friend.objects.filter(user2=aid, user1=f.user1)
            if not friend:
                follower_list.append(f.user1)

        user = User.objects.get(pk=aid)
        response_body = JSONRenderer().render({
            "id": user.host+"/author/"+str(user.id),
            "host": user.host,
            "displayName": user.username,
            "url": user.host+"/author/"+str(user.id),
            "friends": friend_list,
            "friendCount": len(friend_list),
            "followers": follower_list,
            "followerCount": len(follower_list),
            "following": following_list,
            "followingCount": len(following_list),
        })
        return HttpResponse(content=response_body, content_type="application/json", status=200)
    else:
        return HttpResponse(status=405, content="Method Not Allowed")

def grab_external_data():
    #print("Here")
    global request_last_updated
    # Make the request every 60 seconds
    if (time.time() - request_last_updated) > 60:
        # Update the time
        request_last_updated = time.time()
        all_posts_json = []
        for login in RemoteLogin.objects.all():
            response = requests.get("{}{}".format(login.host, "posts"), headers={"Authorization": login.get_authorization()})
        all_posts_json += response.json().get('posts', [])
        #import pdb; pdb.set_trace()
        for post in all_posts_json:
            post
        #print("Make the request: {}".format(request_last_updated))
    else:
        pass
        #print("Don't make the request")

def ensure_data():
    global request_last_updated
    
    if (time.time() - request_last_updated) > 60:
        # Update the time
        request_last_updated = time.time()
        print("Running Request")

        # Get the foreign data first -- this might take a while
        responses = []
        for login in RemoteLogin.objects.all():
            print("-->", login.host)
            try:
                adapter = adapters[login.host]

                response = adapter.get_request(
                        "{}{}".format(login.host, "posts"), login)
                responses.append(response.json())
            except:
                print("Failed to get posts from", login.host)
                continue

        # Delete all foreign posts and comments
        User.objects.filter(local=False).delete()
        Post.objects.filter(local=False).delete()
        Comment.objects.filter(local=False).delete()

            
        for response_json in responses:
            for post in response_json['posts']:
                author_obj = adapter.create_author(post['author'])
                get_foreign_friends(login, author_obj, adapter)
                # if author is created, get it
                post['author'] = author_obj
                
                comments = post['comments']

                # create post before creating comments
                try:
                    post_obj = adapter.create_post(post)

                    for comment in comments:
                        # print("Comment: {}".format(comment))
                        author_obj = adapter.create_author(comment['author'])
                        get_foreign_friends(login, author_obj, adapter)
                        comment['author'] = author_obj
                        comment['post'] = post_obj
                        if not comment['contentType']:
                            comment['contentType'] = 'text/plain'
                        comment_obj = adapter.create_comment(comment)
                        # get or create? save?
                except:
                    print("Rejecting post due to error")

    else:
        pass
        # print("Nope")
        

def get_foreign_friends(login, author, adapter):
    url = adapter.get_friends_path(author)
    #print("URL: {}".format(url))
    response = adapter.get_request(url, login)
    #print("Code: {}".format(response.status_code))
    response_json = response.json()

    for author_id in response_json['authors']:
        #print('Author: {}'.format(author_id))
        url = adapter.get_author_path(author)
        try:
            response = adapter.get_request(url, login)
            response_json = response.json()
            response_json['author'].pop('friends', None)
            adapter.create_author(response_json['author'])
        except Exception as e:
            #raise(e)
            print("BAD")
