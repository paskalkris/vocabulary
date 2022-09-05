from datetime import date

from django.db.models import Subquery, OuterRef
from django.shortcuts import get_list_or_404

from .models import Thesaurus, ThesaurusVersion, ThesaurusItem


class ThesaurusService:
    def get_thesaurus_list(self):
        """
        Получение списка справочников.
        """
        return ThesaurusVersion.objects.all()

    def get_thesaurus_list_actual_to(self, actual_to: date):
        """
        Получение списка справочников, актуальных на указанную дату
        """
        self._validate_parameter_type(actual_to, "actual_to", date)

        subquery = ThesaurusVersion.objects.filter(
            thesaurus=OuterRef("thesaurus"), start_date__lte=actual_to
        ).order_by("-start_date")
        queryset = ThesaurusVersion.objects.filter(
            start_date=Subquery(subquery.values("start_date")[:1])
        )
        return queryset

    def get_thesaurus_current_version_elements(self, thesaurus: Thesaurus):
        """
        Получение элементов заданного справочника текущей версии
        """

        thesaurus_current_version = self._get_thesaurus_current_version(thesaurus)
        return thesaurus_current_version.items.all()

    def validate_elements_thesaurus_current_version(
        self, thesaurus: Thesaurus, code: str = None, value: str = None
    ):
        """
        Валидация элементов заданного справочника текущей версии (проверка на то, что элемент с указанным кодом и значением существует в указанной версии справочника.)
        """
        thesaurus_current_version = self._get_thesaurus_current_version(thesaurus)
        return self.validate_elements_thesaurus_version(
            thesaurus_current_version, code, value
        )

    def get_thesaurus_version_elements(self, thesaurus_version: ThesaurusVersion):
        """
        Получение элементов заданного справочника указанной версии
        """
        self._validate_parameter_type(
            thesaurus_version, "thesaurus_version", ThesaurusVersion
        )

        return thesaurus_version.items.all()

    def validate_elements_thesaurus_version(
        self, thesaurus_version: ThesaurusVersion, code: str = None, value: str = None
    ):
        """
        Валидация элемента заданного справочника по указанной версии
        """
        self._validate_parameter_type(
            thesaurus_version, "thesaurus_version", ThesaurusVersion
        )
        filters = {k: v for k, v in (("code", code), ("value", value)) if v}
        if filters:
            return get_list_or_404(
                ThesaurusItem, thesaurus_version=thesaurus_version, **filters
            )
        raise AttributeError("None of the parameters specified (code and value)")

    def _get_thesaurus_current_version(self, thesaurus: Thesaurus):
        """
        Получение справочника текущей версии
        """
        self._validate_parameter_type(thesaurus, "thesaurus", Thesaurus)

        today = date.today()
        thesaurus_current_version = self.get_thesaurus_list_actual_to(today).get(
            thesaurus=thesaurus
        )
        return thesaurus_current_version

    def _validate_parameter_type(self, parameter, parameter_name, expected_type):
        if type(parameter) is not expected_type:
            raise TypeError(
                f"'{parameter_name}' parameter is {type(parameter)}, expected '{expected_type}'"
            )
