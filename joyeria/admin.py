from django.contrib import admin
from .models import *

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ["Nombre", "precio", "categoria","material","stock"]
    list_editable = ["precio"]
    search_fields = ["nombre","stock"]
    list_filter = ["categoria"]
    list_per_page = 10

admin.site.register(Categoria)
admin.site.register(Material)
admin.site.register(Productos, ProductoAdmin)
admin.site.register(Comentarios)
admin.site.register(Carro)
admin.site.register(DireccionEnvio)
admin.site.register(Pagos)
admin.site.register(Pedidos)
admin.site.register(DetallePedido)
