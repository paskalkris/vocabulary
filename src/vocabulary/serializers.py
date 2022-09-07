from rest_framework import serializers

from .models import Thesaurus, ThesaurusVersion, ThesaurusItem


class ThesaurusVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThesaurusVersion
        exclude = ["thesaurus"]


class ThesaurusSerializer(serializers.ModelSerializer):
    versions = ThesaurusVersionSerializer(many=True)

    class Meta:
        model = Thesaurus
        fields = "__all__"


class ThesaurusItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThesaurusItem
        exclude = ["thesaurus_version"]
