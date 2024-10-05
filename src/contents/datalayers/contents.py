from src.contents.models import Content, Author, Tag
from django.utils import timezone
from django.db.models import F, When, Case, IntegerField, Value, Sum, Count
from django.contrib.postgres.aggregates import ArrayAgg
from datetime import timedelta
import pytz

class ContentDatalayer(object):

    @classmethod
    def get_current_time(cls, timezone_string='Asia/Dhaka'):
        return timezone.now().astimezone(pytz.timezone(timezone_string))

    @classmethod
    def get_start_end_index(cls, page, size):
        start = page * size
        end = start + size
        return start, end, page, size


    @classmethod
    def filter_content(
            cls, tag=None, author_id=None, author_username=None, timeframe=None, title=None
    ):

        queryset = Content.objects.select_related('author').all()
        
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        if author_username:
            queryset = queryset.filter(author__username=author_username)

        if tag:
            queryset = queryset.filter(contenttag__tag__name=tag).distinct()

        if timeframe:
            end_time = cls.get_current_time()
            st_time = end_time - timedelta(days=timeframe)

            queryset = queryset.filter(timestamp__range=[st_time, end_time])

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    @classmethod
    def get_content_details(
            cls, tag=None, author_id=None, author_username=None, timeframe=None, title=None
    ):

        contents = cls.filter_content(
            tag=tag, author_id=author_id, author_username=author_username, timeframe=timeframe, title=title
        )

        contents = contents.annotate(
            total_engagement=F('like_count') + F('comment_count') + F('share_count'),
            view_count=F('view_count'),
            tags=ArrayAgg('tag__name', default=[])
        )

        contents = contents.annotate(
            engagement_rate=Case(
                When(
                    view_count__gt=0,
                    then=F('total_engagement')/F('view_count')
                ),
                default=Value(0), output_field=IntegerField(),
            )
        )

        return contents.order_by('-timestamp')


    @classmethod
    def get_content_stat(
            cls, tag=None, author_id=None, author_username=None, timeframe=None, title=None
    ):
        contents = cls.filter_content(
            tag=tag, author_id=author_id, author_username=author_username, timeframe=timeframe, title=title
        )

        contents = contents.aggregate(
            total_likes=Sum('like_count', default=0),
            total_shares=Sum('share_count', default=0),
            total_views=Sum('view_count', default=0),
            total_comments=Sum('comment_count', default=0),
            total_contents=Count('id', default=0),
            total_followers=Sum('author__followers', default=0)
        )


        contents['total_engagement'] = contents['total_likes'] + contents['total_shares'] + contents['total_comments']

        contents['total_engagement_rate'] = contents['total_engagement']/contents['total_views'] if contents['total_views']>0 else 0

        return contents


    @classmethod
    def create_content_post(cls, list_data):

        content_list = []

        for data in list_data.get('contents'):

            if Author.objects.filter(
                unique_id=data['author']["unique_external_id"]
            ).exists():

                author_object = Author.objects.get(unique_id=data['author']['unique_external_id'])
            else:

                author_object = Author(
                    username=data['author']['unique_name'],
                    name=data['author']['full_name'],
                    unique_id=data['author']['unique_external_id'],
                    url=data['author']['url'],
                    title=data['author']['title'],
                    big_metadata=data['author']['big_metadata'],
                    secret_value=data['author']['secret_value']
                )

                author_object.save()


            if Content.objects.filter(
                unique_id=data["unq_external_id"]
            ).exists():
                content_object = Content.objects.get(unique_id=data["unq_external_id"])

            else:
                content_object =Content(
                    unique_id=data['unq_external_id'],
                    author=author_object,
                    title=data['title'],
                    big_metadata=data['big_metadata'],
                    secret_value=data['secret_value'],
                    thumbnail_url=data['thumbnail_view_url'],
                    like_count=data["stats"]["likes"],
                    comment_count=data["stats"]["comments"],
                    share_count=data["stats"]["shares"],
                    view_count=data["stats"]["views"]
                )

                content_object.save()

            for tag in data.get("hashtags"):

                tag_object = Tag.objects.filter(name=tag).first()

                if not tag_object:
                    tag_object = Tag(name=tag)
                    tag_object.save()

                content_object.contenttag.add(tag_object)

            content_list.append(
                dict(
                    content=content_object,
                    author=author_object
                )
            )

        return content_list











