from django.core.paginator import Paginator


def paginator_my(request, posts, quantity_of_posts_on_page):
    paginator = Paginator(posts, quantity_of_posts_on_page)
    page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    return paginator.get_page(page_number)
