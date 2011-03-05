from django.contrib import admin

from catalog.models import Products, ProductsPhoto, Categories, Sections, Features, FeaturesName
from cart.models import Clients

class PhotoInline(admin.StackedInline):
    model = ProductsPhoto

class FeaturesInline(admin.StackedInline):
    model = Features

admin.site.register(ProductsPhoto)

class ProductsAdmin(admin.ModelAdmin):
    inlines = [PhotoInline, FeaturesInline]
    list_display = ('name', 'price', 'created_at', 'updated_at',)
    list_display_links = ('name',)
    list_per_page = 50
    ordering = ['-created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug' : ('name',)}

admin.site.register(Products, ProductsAdmin)

class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at',)
    list_display_links = ('name',)
    list_per_page = 20
    ordering = ['name']
    search_fields = ['name', 'description',]
    prepopulated_fields = {'slug' : ('name',)}

admin.site.register(Categories, CategoriesAdmin)

class SectionsAdmin(admin.ModelAdmin):
        prepopulated_fields = {'slug' : ('name',)}

admin.site.register(Sections, SectionsAdmin)

admin.site.register(FeaturesName)

class ClientsAdmin(admin.ModelAdmin):
    ordering = ['ordered_at']
    list_display = ('ordered_at', 'name')

admin.site.register(Clients, ClientsAdmin)
