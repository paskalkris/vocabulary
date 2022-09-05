from datetime import date

from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Thesaurus, ThesaurusVersion
from .serializers import ThesaurusVersionSerializer, ThesaurusItemSerializer
from .service import ThesaurusService


class ThesaurusAPIView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ThesaurusVersionSerializer
    thesaurus_service = ThesaurusService()

    def get_queryset(self):
        actual_to = self._get_date_param("actual_to")

        if actual_to:
            return self.thesaurus_service.get_thesaurus_list_actual_to(actual_to)

        return self.thesaurus_service.get_thesaurus_list()

    def _get_date_param(self, name: str) -> date | None:
        date_str = self.request.query_params.get(name)
        if not date_str:
            return

        try:
            return parse_date(date_str)
        except ValueError:
            raise ValidationError(f"Parameter '{name}' is not valid")


class ThesaurusItemAPIView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ThesaurusItemSerializer
    thesaurus_service = ThesaurusService()

    def get_queryset(self):
        thesaurus_slug = self.kwargs["thesaurus"]
        thesaurus_version_slug = self.kwargs.get("version")

        code = self.request.query_params.get("code")
        value = self.request.query_params.get("value")

        thesaurus = get_object_or_404(Thesaurus, slug=thesaurus_slug)
        if thesaurus_version_slug:
            thesaurus_version = get_object_or_404(
                ThesaurusVersion, thesaurus=thesaurus, slug=thesaurus_version_slug
            )

            if code or value:
                return self.thesaurus_service.validate_elements_thesaurus_version(
                    thesaurus_version, code, value
                )

            return self.thesaurus_service.get_thesaurus_version_elements(
                thesaurus_version
            )

        if code or value:
            return self.thesaurus_service.validate_elements_thesaurus_current_version(
                thesaurus, code, value
            )

        return self.thesaurus_service.get_thesaurus_current_version_elements(thesaurus)
