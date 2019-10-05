from datetime import datetime

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class NoticePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        return self.page.next_page_number()

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        return self.page.previous_page_number()

    def paginate_queryset(self, queryset, request, view=None):

        if request.query_params.get('after'):
            queryset = queryset.filter(
                created_at__lt=request.query_params.get('after'))

        # if request.query_params.get('after'):
        #     queryset = queryset.filter(
        #         created_at__lte=datetime.strptime(request.query_params.get('after'), "%d-%m-%Y, %H:%M"))
        # queryset = queryset.filter()
        # queryset = self.filter_queryset(self.queryset.filter(course=pk))
        return super().paginate_queryset(queryset, request, view)
