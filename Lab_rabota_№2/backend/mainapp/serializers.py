from rest_framework import serializers
from .models import Nerf

#В файле serializers.py хранятся сериализаторы. Сериализаторы преобразуют данные из одного формата в другой.



#В данном случае происходит преобразование данных из python в JSON.
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nerf
        fields = '__all__'


