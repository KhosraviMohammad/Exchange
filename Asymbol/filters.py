import datetime

import django_filters

from Asymbol.models import Slope


class SlopeFilter(django_filters.FilterSet):
    value = django_filters.NumericRangeFilter(field_name='value')

    class Meta:
        model = Slope
        fields = ['value', 'from_date']


