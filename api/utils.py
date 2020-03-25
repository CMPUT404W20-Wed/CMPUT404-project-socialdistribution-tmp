from django.core.paginator import Paginator
from .models import Post, User, Comment, RemoteLogin
import copy

def create_pagination_info(request, objects_paginator: Paginator, page, size, filter_):
    uri = request.build_absolute_uri()
    info = dict()
    if page > 1 and objects_paginator.page(page).has_previous():
        prev = "{}?page={}&size={}&filter=".format(uri, objects_paginator.previous_page_number(), size, filter_)
        info["previous"] = prev
    if objects_paginator.page(page).has_next():
        next = "{}?page={}&size={}&filter=".format(uri, objects_paginator.next_page_number(), size, filter_)
        info["next"] = next
    return info

def get_post_query_params(request):
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 50))
    filter_ = request.GET.get('filter', '')
    return page, size, filter_

class Group4Adapter:

    def __init__(self):
        self.path = "https://cmput404-group-project-mandala.herokuapp.com/"

    def create_author(self, author_json):
        # print('Author: {}'.format(author_json))
        id = author_json['id'].split('/')[-1]
        author_json['id'] = id
        author_obj = User(**author_json)
        author_obj.username = author_json['displayName']
        author_obj.password = ""
        author_obj.save()
        return author_obj

    def create_post(self, post_json):
        post_json_d = copy.deepcopy(post_json)
        # print("Post: {}".format(post_json))
        id = post_json_d['id']
        # post_json_d['author'] = self.create_author(post_json_d['author'])
        post_json_d['local'] = False
        del post_json_d['count']
        del post_json_d['next']
        del post_json_d['comments']

        post_obj = Post(**post_json_d)
        post_obj.save()
        return post_obj

    def create_comment(self, comment_json):
        #print("Comment: {}".format(comment_json))
        id = comment_json['id']
        comment_json['local'] = False
        comment_obj = Comment(**comment_json)
        
        comment_obj.save()
        return comment_obj

    def get_friends_path(self, author):
        path = self.path + 'author/' + author.id.split('/')[-1] + '/friends'
        return path

    def get_author_path(self, author):
        path = self.path + 'author/' + author.id.split('/')[-1]
        return path

class Group3Adapter:

    def __init__(self):
        self.path = "http://dsnfof.herokuapp.com/api/"

    def create_author(self, author_json):
        # print('Author: {}'.format(author_json))
        id = author_json['id'].split('/')[-1]
        author_json['id'] = id
        author_obj = User(**author_json)
        author_obj.username = author_json['displayName']
        author_obj.password = ""
        author_obj.save()
        return author_obj

    def create_post(self, post_json):
        post_json_d = copy.deepcopy(post_json)
        # print("Post: {}".format(post_json))
        id = post_json_d['id']
        # post_json_d['author'] = self.create_author(post_json_d['author'])
        post_json_d['local'] = False
        del post_json_d['count']
        del post_json_d['next']
        del post_json_d['comments']

        post_obj = Post(**post_json_d)
        post_obj.save()
        return post_obj

    def create_comment(self, comment_json):
        #print("Comment: {}".format(comment_json))
        id = comment_json['id']
        comment_json['local'] = False
        comment_obj = Comment(**comment_json)
        
        comment_obj.save()
        return comment_obj

    def get_friends_path(self, author):
        path = self.path + 'author/' + author.id.split('/')[-1] + '/friends'
        return path

    def get_author_path(self, author):
        path = self.path + 'author/' + author.id.split('/')[-1]
        return path

# initialize the adapters for the groups
group3adapter = Group3Adapter()
group4adapter = Group4Adapter()

adapters = {
    "https://dsnfof.herokuapp.com/api/": group3adapter,
    "https://cmput404-group-project-mandala.herokuapp.com/": group4adapter
}

'''

'''
'''
creds = LocalLogin.objects.filter(pk=request.get_host())

creds_authed = False

if creds:

    creds_authed = creds.get_authetication() == request.content_params.get('Authorization', '')

if not creds_authed or request.user.is_authenticated()
'''
'''

if method == "GET":

    page, size, filter_ = get_post_query_params(request)

    all_posts_json = []

    for login in RemoteLogin.objects.all():

        response = requests.get("{}{}?page={}&size={}&filter={}".format(login.host, "posts", page,size,filter_), headers={"Authorization": login.get_authorization()})

        all_posts_json += response.json().get('posts', [])

        

    for post in all_posts_json:

        post['author']['id'] = post['author']['id'].split('/')[-1]

        post['author'] = User(**post['author'])

        del post['count']

        del post['next']

        comments = post['comments']

        

        # save the author

        # for comment in comments, save

        # delete the comment field from the post

        # save the post

        # set the foreginkey to the post

    all_posts_objects = [Post(**post) for post in all_posts_json]

'''