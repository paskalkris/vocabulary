from rest_framework import serializers

from .models import Thesaurus, ThesaurusVersion, ThesaurusItem


class ThesaurusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thesaurus
        fields = "__all__"


class ThesaurusVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThesaurusVersion
        fields = "__all__"
        depth = 1


class ThesaurusItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThesaurusItem
        exclude = ["thesaurus_version"]
