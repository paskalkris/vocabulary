from datetime import date
import json

from django.urls import reverse
from django.test import TestCase
from rest_framework import status

from .models import Thesaurus, ThesaurusVersion, ThesaurusItem
from .service import ThesaurusService


class ThesaurusTestCase(TestCase):
    def setUp(self):
        with open("_test_initial_data.json") as f:
            initial_data = json.load(f)

        self.thesauruses = []
        for thesaurus_raw in initial_data:
            versions = thesaurus_raw.pop("versions")

            thesaurus = Thesaurus.objects.create(**thesaurus_raw)
            self.thesauruses.append(thesaurus)

            for version_raw in versions:
                items = version_raw.pop("items")
                version_raw["thesaurus"] = thesaurus

                version = ThesaurusVersion.objects.create(**version_raw)

                for item_raw in items:
                    item_raw["thesaurus_version"] = version

                    ThesaurusItem.objects.create(**item_raw)


class ThesaurusAPIViewTests(ThesaurusTestCase):
    def test_get_thesaurus_list(self):
        """
        Получение списка справочников.
        """
        response = self.client.get(reverse("thesaurus-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 6)

    def test_get_thesaurus_list_actual_to(self):
        """
        Получение списка справочников, актуальных на указанную дату
        """
        actual_to = date.today()
        response = self.client.get(reverse("thesaurus-list"), {"actual_to": actual_to})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        actual_to = date(2022, 8, 15)
        response = self.client.get(reverse("thesaurus-list"), {"actual_to": actual_to})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        actual_to = date(2022, 7, 15)
        response = self.client.get(reverse("thesaurus-list"), {"actual_to": actual_to})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_empty_thesaurus_list_actual_to(self):
        """
        Получение списка справочников, актуальных на указанную дату
        В качестве параметра передаем дату, для которой нет словарей
        """
        actual_to = date(2020, 7, 15)
        response = self.client.get(reverse("thesaurus-list"), {"actual_to": actual_to})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_get_empty_thesaurus_list_actual_to_wrong_date(self):
        """
        Получение списка справочников, актуальных на указанную дату
        В качестве параметра передаем в качестве даты неверное значение
        """
        response = self.client.get(reverse("thesaurus-list"), {"actual_to": "jhkjhk"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 6)

        response = self.client.get(
            reverse("thesaurus-list"), {"actual_to": "2022-13-01"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], "Parameter 'actual_to' is not valid")

    def test_send_not_allowed_method(self):
        """
        Проверка обработки неподдерживаемых методов.
        """
        response = self.client.post(f'{reverse("thesaurus-list")}')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json(), {"detail": 'Метод "POST" не разрешен.'})


class ThesaurusItemAPIViewTests(ThesaurusTestCase):
    def test_get_thesaurus_current_version_elements(self):
        """
        Получение элементов заданного справочника текущей версии
        """
        url = reverse("thesaurus-item-list", kwargs={"thesaurus": "ias-smo"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_get_thesaurus_current_version_elements_wrong_thesaurus(self):
        """
        Получение элементов заданного справочника текущей версии: не существующий справочник
        """
        url = reverse("thesaurus-item-list", kwargs={"thesaurus": "wrong-thesaurus"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_validate_element_thesaurus_current_version(self):
        """
        Валидация элементов заданного справочника текущей версии (проверка на то, что элемент с указанным кодом и значением существует в указанной версии справочника.)
        """
        url = reverse("thesaurus-item-list", kwargs={"thesaurus": "ias-smo"})
        response = self.client.get(url, {"code": "123", "value": "Элемент 123"})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(len(response.data["results"]), 1)

    def test_validate_element_thesaurus_current_version_wrong_code(self):
        """
        Валидация элементов заданного справочника текущей версии: не существующий код
        """
        url = reverse("thesaurus-item-list", kwargs={"thesaurus": "ias-smo"})
        response = self.client.get(url, {"code": "1231234sdfs"})

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND, response.json()
        )

    def test_validate_element_thesaurus_current_version_wrong_thesaurus(self):
        """
        Валидация элементов заданного справочника текущей версии: не существующий справочник
        """
        url = reverse("thesaurus-item-list", kwargs={"thesaurus": "wrong-thesaurus"})
        response = self.client.get(url, {"code": "123", "value": "Элемент 123"})

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND, response.json()
        )

    def test_get_thesaurus_version_elements(self):
        """
        Получение элементов заданного справочника указанной версии
        """
        url = reverse(
            "thesaurus-version-item-list",
            kwargs={"thesaurus": "ias-smo", "version": "101"},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_get_thesaurus_version_elements_wrong_version(self):
        """
        Получение элементов заданного справочника указанной версии: не существующая версия
        """
        url = reverse(
            "thesaurus-version-item-list",
            kwargs={"thesaurus": "ias-smo", "version": "wrong-version"},
        )
        response = self.client.get(url)

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND, response.json()
        )

    def test_validate_element_thesaurus_version(self):
        """
        Валидация элемента заданного справочника по указанной версии
        """
        url = reverse(
            "thesaurus-version-item-list",
            kwargs={"thesaurus": "ias-smo", "version": "101"},
        )
        response = self.client.get(url, {"code": "125", "value": "Элемент 125"})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertEqual(len(response.data["results"]), 1)


class ThesaurusServiceTests(ThesaurusTestCase):
    thesaurus_service = ThesaurusService()

    def test_get_thesaurus_list(self):
        """
        Получение списка справочников.
        """
        result = self.thesaurus_service.get_thesaurus_list()
        self.assertEqual(len(result), 6)

    def test_get_thesaurus_list_actual_to(self):
        """
        Получение списка справочников, актуальных на указанную дату
        """
        actual_to = date.today()
        result = self.thesaurus_service.get_thesaurus_list_actual_to(actual_to)
        self.assertEqual(len(result), 2)

        actual_to = date(2022, 8, 15)
        result = self.thesaurus_service.get_thesaurus_list_actual_to(actual_to)
        self.assertEqual(len(result), 2)

        actual_to = date(2022, 7, 15)
        result = self.thesaurus_service.get_thesaurus_list_actual_to(actual_to)
        self.assertEqual(len(result), 1)

    def test_get_thesaurus_current_version_elements(self):
        """
        Получение элементов заданного справочника текущей версии
        """
        result = self.thesaurus_service.get_thesaurus_current_version_elements(
            self.thesauruses[0]
        )
        self.assertEqual(len(result), 2)

    def test_validate_element_thesaurus_current_version(self):
        """
        Валидация элементов заданного справочника текущей версии (проверка на то, что элемент с указанным кодом и значением существует в указанной версии справочника.)
        """
        result = self.thesaurus_service.validate_elements_thesaurus_current_version(
            self.thesauruses[0], code="123", value="Элемент 123"
        )
        self.assertEqual(result[0], self.thesauruses[0].versions.first().items.first())

    def test_get_thesaurus_version_elements(self):
        """
        Получение элементов заданного справочника указанной версии
        """
        result = self.thesaurus_service.get_thesaurus_version_elements(
            self.thesauruses[0].versions.all()[1]
        )
        self.assertEqual(len(result), 3)

    def test_validate_element_thesaurus_version(self):
        """
        Валидация элемента заданного справочника по указанной версии
        """
        result = self.thesaurus_service.validate_elements_thesaurus_version(
            self.thesauruses[0].versions.all()[1], code="125", value="Элемент 125"
        )
        self.assertEqual(
            result[0], self.thesauruses[0].versions.all()[1].items.all()[2]
        )
