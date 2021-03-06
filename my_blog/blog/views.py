from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator

from django.views.generic import TemplateView, ListView, DetailView,\
    CreateView, UpdateView, DeleteView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Comment, About, Story, ReaderInfo

# Create your views here.


class AboutDetailView(ListView):
    """A view that contains some information about the blog or the author or the organization"""
    model = About

    def get_queryset(self):
        return About.objects.all()


def post_list_view(request):
    """
    This view returns to a page where the list of all the posts are available.
    We can think this as the home page. The posts are available in descending time order.
    """
    post_list = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    comments = len(Comment.objects.filter(approved_comment=False).order_by('-created_date'))

    if comments > 0:
        return render(request, 'blog/post_list.html', context={'comments': comments, 'page_obj': page_obj})
    else:

        return render(request, 'blog/post_list.html', context={'page_obj': page_obj})


def post_detail_view(request, pk):
    """
    Upon clicking on a post this view will take to a page where all the detail about that
    post is available. One will read a post from this view. Also the reader info about that
    particular post will be added from here.
    """
    post = Post.objects.get(pk=pk)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    readerinfo = ReaderInfo(post=post,user_ip=ip)
    readerinfo.save()

    return render(request, 'blog/post_detail.html', context={'post':post})


@login_required
def create_post(request, pk):
    """
    This view creates a new post and add a new entry to Post model.
    """
    story = Story.objects.get(pk=pk)
    if request.method=='POST':
        title = request.POST['title']
        text = request.POST['text']

        post = Post(story=story, title=title, text=text)
        post.save()
        return redirect('story_parts', pk=pk)

    return render(request, 'blog/post_form.html', context={'story_name': story.story_name,
                                                           'pk': pk})


@login_required
def post_update_view(request, pk):
    """
    This model updates a particular post and save the update in the Post model.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method=='POST':
        title = request.POST['title']
        text = request.POST['text']
        post.title=title
        post.text=text
        post.save()
        messages.success(request, message="Successfully updated!")
        return redirect('post_detail', pk=pk)

    return render(request, 'blog/post_edit.html', context={'post':post})


# =====================Story=============================
class StoryListView(ListView):
    """
    Shows the list of all the stories.
    """
    model = Story
    context_object_name = 'stories'


def story_part_list_view(request, pk):
    """
    Shows the list of all the entries of a particular story. Or we can say the list of
    all the episodes in a story.
    """
    story = Story.objects.get(pk=pk)
    story_parts = Post.objects.filter(story=story).order_by('-create_date')

    return render(request, 'blog/story_part_list.html', context={'story_parts':story_parts,
                                                                 'story': story})

@login_required
def create_new_story(request):
    """
    This view creates a new story and create a new entry to Story model.
    """
    author = request.user
    if request.method=='POST':
        story_name = request.POST['name']
        story_trailer = ''
        if request.POST['trailer']:
            story_trailer = request.POST['trailer']

        story = Story(author=author, story_name=story_name, story_trailer=story_trailer)

        story.save()

        return redirect('story_parts', pk=story.pk)

    return render(request, 'blog/new_story_form.html')


class StoryDeleteView(LoginRequiredMixin, DeleteView):
    """
    This view deletes a story from the database.
    """
    model = Story
    success_url = reverse_lazy('stories')


@login_required
def story_update_view(request, pk):
    """
    This view updates any information about a particular story such as story name/story trailer.
    """
    story = get_object_or_404(Story, pk=pk)
    if request.method=='POST':
        story_name = request.POST['name']
        story_trailer = request.POST['trailer']
        story.story_name = story_name
        story.story_trailer = story_trailer
        story.save()
        messages.success(request, message="Successfully updated!")
        return redirect('story_parts', pk=pk)

    return render(request, 'blog/story_edit.html', context={'story':story})

# =====================End Story=============================


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """
    Deletes a post from the database.
    """
    model = Post
    success_url = reverse_lazy('post_list')


def draft_list_view(request):
    """
    Shows the list of all the yet to be published post.
    """
    posts = Post.objects.filter(published_date__isnull=True).order_by('-create_date')

    return render(request, 'blog/draft_list.html', context={'posts': posts})


@login_required
def draft_detail_view(request, pk):
    """
    Shows detail about a particular yet to be published post.
    """
    post = Post.objects.filter(pk=pk)[0]
    return render(request, 'blog/draft_detail.html', context={'post':post})


class InstructionsView(TemplateView):
    template_name = 'blog/instructions.html'


###############################################################
###############################################################


@login_required
def post_publish(request, pk):
    """
    This view publish a particular post from yet to be published list.
    """
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


def add_comment_to_post(request, pk):
    """
    The view creates a new entry upon adding a comment to a post.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method=='POST':
        author = request.POST['author']
        text = request.POST['text']
        comment = Comment(post=post, author=author, text=text)
        comment.save()
        messages.success(request, message="Your comment will pop up upon author's approval")
        return redirect('post_detail', pk=pk)


@login_required
def comment_approve(request, pk):
    """
    This view approve a comment upon author's approval.
    """
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    messages.success(request, message="Comment approved!")
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    """
    This views removes a comment upon author's removal.
    """
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    messages.success(request, message="Comment removed!")
    return redirect('post_detail', pk=post_pk)


@login_required
def notifications(request):
    comments = Comment.objects.filter(approved_comment=False).order_by('-created_date')
    print(comments[0].author)
    return render(request, 'blog/notifications.html', context={'comments': comments})