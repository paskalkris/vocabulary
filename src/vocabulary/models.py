from django.db import models


class Thesaurus(models.Model):
    name = models.CharField("Наименование", max_length=255, unique=True)
    short_name = models.CharField("Краткое наименование", max_length=31, unique=True)
    slug = models.CharField("URL", max_length=31, db_index=True, unique=True)
    description = models.TextField("Описание", blank=True)
    is_actual = models.BooleanField("Актуален", default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "thesaurus"
        verbose_name = "Справочник"
        verbose_name_plural = "Справочники"
        ordering = ["name"]


class ThesaurusVersion(models.Model):
    thesaurus = models.ForeignKey(
        to=Thesaurus,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name="Справочник",
    )
    version = models.CharField("Версия", max_length=31)
    start_date = models.DateField("Действует с")
    slug = models.CharField("URL", max_length=31, db_index=True)

    def __str__(self):
        return f"[{self.version} от {self.start_date}] {self.thesaurus}"

    class Meta:
        db_table = "thesaurus_version"
        unique_together = [
            ["thesaurus", "version"],
            ["thesaurus", "start_date"],
            ["thesaurus", "slug"],
        ]
        verbose_name = "Версия справочника"
        verbose_name_plural = "Версии справочников"
        ordering = ["thesaurus", "-start_date"]


class ThesaurusItem(models.Model):
    thesaurus_version = models.ForeignKey(
        to=ThesaurusVersion,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Справочник",
    )
    code = models.CharField("Код", max_length=31)
    value = models.CharField("Значение", max_length=255)

    def __str__(self):
        return f"[{self.code}] {self.value}"

    class Meta:
        db_table = "thesaurus_item"
        unique_together = [
            ["thesaurus_version", "code"],
            ["thesaurus_version", "value"],
        ]
        verbose_name = "Элемент справочника"
        verbose_name_plural = "Элементы справочников"
        ordering = ["thesaurus_version", "value"]
