from datetime import date

from django.contrib import admin

from . import models


class ThesaurusItemInline(admin.TabularInline):
    model = models.ThesaurusItem


class ThesaurusAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "short_name", "description", "is_actual")
    list_display_links = ("id", "name")
    search_fields = ("name", "short_name")
    list_editable = ("is_actual",)
    list_filter = ("is_actual",)
    prepopulated_fields = {"slug": ("short_name",)}


class ThesaurusVersionAdmin(admin.ModelAdmin):
    filds = ("thesaurus", "version", "start_date")
    list_display = ("id", "thesaurus", "version", "start_date")
    list_display_links = ("id", "thesaurus", "version")
    search_fields = ("thesaurus", "version")
    list_filter = ("thesaurus",)
    prepopulated_fields = {"slug": ("version",)}
    inlines = [
        ThesaurusItemInline,
    ]

    def get_changeform_initial_data(self, request):
        return {"start_date": date.today()}


class ThesaurusItemAdmin(admin.ModelAdmin):
    list_display = ("id", "thesaurus_version", "code", "value")
    list_display_links = ("id", "value")
    search_fields = ("thesaurus_version", "code", "value")
    list_filter = ("thesaurus_version",)


admin.site.register(models.Thesaurus, ThesaurusAdmin)
admin.site.register(models.ThesaurusVersion, ThesaurusVersionAdmin)
admin.site.register(models.ThesaurusItem, ThesaurusItemAdmin)
