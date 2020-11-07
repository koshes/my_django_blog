from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Поиск по нескольким полям
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Count
from django.shortcuts import render, get_object_or_404

from blog.models import Comment, Post
from blog.forms import CommentForm, EmailPostForm, SearchForm
from my_django_blog.settings import EMAIL_HOST_USER

from taggit.models import Tag


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    # количество постов на странице
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если номер страницы не int - переход на первую первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если страница выходит за пределы допустимого диапазона - переход на последнюю страницу
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # Список активных комментариев к этому посту
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # Комментарий опубликован
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создать объект, но пока не сохранять в базу данных
            new_comment = comment_form.save(commit=False)
            # Назначить текущий пост комментарию
            new_comment.post = post
            # Сохранить комментарий в базе данных
            new_comment.save()
    else:
        comment_form = CommentForm()
    # Список похожих постов
    post_tags_ids = post.tags.values_list('id', flat=True)
    # Получить посты, которые содержат любые из этих тегов, исключая текущий.
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts})


def post_share(request, post_id):
    # Поиск поста по id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"Пользователь {cd['name']} рекомендует Вам прочитать {post.title}"
            message = f"Прочитайте статью {post.title} по ссылке {post_url}\n\n " \
                      f"Коментарии пользователя {cd['name']}: {cd['comments']}"
            send_mail(subject, message, EMAIL_HOST_USER, [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


def post_search(request):
    # Поиск постов по названию и тексту
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # Установка большего веса вектора поиска для title для повышения релевантности
            search_vector = SearchVector('title', weight='A') + \
                SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.3).order_by('-rank')
    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})
