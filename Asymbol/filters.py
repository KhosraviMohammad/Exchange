import datetime

import django_filters

from Asymbol.models import Slope


class SlopeFilter(django_filters.FilterSet):
    value_from = django_filters.NumberFilter(field_name='value', lookup_expr='gte')
    value_to = django_filters.NumberFilter(field_name='value', lookup_expr='lte')
    from_date_start = django_filters.DateTimeFilter(field_name='from_date', lookup_expr='gte')
    from_date_end = django_filters.DateTimeFilter(field_name='from_date', lookup_expr='lte')

    class Meta:
        model = Slope
        fields = ['value_from', 'value_to', 'from_date_start', 'from_date_end']
