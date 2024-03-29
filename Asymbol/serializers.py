from rest_framework import serializers
from Asymbol.models import Slope
import pytz

class SlopeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    symbol_name = serializers.CharField(read_only=True)
    value = serializers.CharField(read_only=True)
    from_date = serializers.DateTimeField(read_only=True, default_timezone=pytz.timezone('UTC'))
    to_date = serializers.DateTimeField(read_only=True, default_timezone=pytz.timezone('UTC'))

    class Meta:
        model = Slope
        fields = ['id', 'symbol_name', 'value', 'from_date', 'to_date']
