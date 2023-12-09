from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
app_name = 'tienda'

urlpatterns = [
    path('', views.index, name='index'),
#Productos
    # Categorias
    path('categorias/', views.ListarCategorias, name='listar_categorias'),
    path('categorias-agregar/', views.AgregarCategoria, name='agregar_categoria'),
    path('categorias/<str:nombre>/modificar/', views.ModificarCategoria, name='modificar_categoria'),  # Cambia de slug a nombre
    path('categorias/<str:nombre>/', views.eliminar_categorias, name='eliminar_categorias'),  # Cambia de slug a nombre
    
    # Productos
    path('producto/<str:nombre>/', views.detalleProducto, name='producto'), 
    path('listar-productos/', views.listar_productos, name='listar_productos'),
    path('agregar-productos/', views.agregar_producto, name='agregar_producto'),
    path('eliminar-productos/<str:nombre>/', views.eliminar_producto, name='eliminar_producto'),  
    path('modificar-productos/<str:nombre>/', views.modificar_producto, name='modificar_producto'),  
    path('productocategoria/<str:nombre>/', views.productoxCategoria, name='productocategoria'), 

#inicio y registro de usuario
    path('registrar/', views.registro, name='registrar'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

#carro de compras

    path('addtocart/<int:producto_id>/', views.add_to_cart, name='addtocart'),
    path('cart/', views.cart_page, name='cart'),
    path('procesar_pedido/', views.procesar_pedido, name='procesar_pedido'),
    path('lista-pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('materiales/', views.mostrar_materiales, name='mostrar_materiales'),
    path('materiales/agregar/', views.agregar_material, name='agregar_material'),
    path('materiales/editar/<int:material_id>/', views.editar_material, name='editar_material'),
    path('materiales/eliminar/<int:material_id>/', views.eliminar_material, name='eliminar_material'),

    path('comentarios/', views.listar_comentarios, name='listar_comentarios'),
    path('comentarios/eliminar/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),

    path('eliminar_items_carrito/', views.eliminar_items_carrito, name='eliminar_items_carrito'),
    path('panel/', views.panel, name='panel'),
    path('editar_perfil/<int:user_id>/', views.editar_perfil, name='editar_perfil'),
    path('<int:pk>/password/', views.CustomPasswordChangeView.as_view(), name='password_change'),


    path('ubicacion/', views.ubicacion, name='ubicacion'),
    path('ubicacion-nuevas/', views.ubicacion_nuevas, name='ubicacion-nuevas'),
    path('ubicacion-editar/<int:id>/modificar/', views.editar_ubicacion, name='ubicacion-editar'),
    path('ubicacion-eliminar/<int:id>', views.eliminar_ubicacion, name='ubicacion-eliminar'),
    
    path('valoraciones/', views.valoraciones, name='valoraciones'),

    path('ajustes/', views.ajustes, name='ajustes'),

    path('contacto/', views.contacto, name='contacto'),
    path('listarcontacto/', views.mostrar_contacto, name='listarcontacto'),
    path('detallecontacto/<id>/', views.detalle_contacto, name='detallecontacto'),
    path('deletecontacto/<id>/', views.eliminar_contacto, name='deletecontacto'),


    path('solgas/usuario/administrar/', views.usuario_administrar, name='usuarioadministrar'),
    path('solgas/usuario/modificar/<int:id>/',views.usuario_administrar_modificar),
    path('solgas/usuario/eliminar/<int:id>/',views.usuario_administrar_eliminar),
    path('solgas/crearusuario/',views.crear_usuario),

   path('carrucel/', views.carrucel_list, name='carrucel_list'),
    path('carrucel/<int:id>/', views.carrucel_detail, name='carrucel_detail'),
    path('carrucel/create/', views.carrucel_create, name='carrucel_create'),
    path('carrucel/<int:id>/update/', views.carrucel_update, name='carrucel_update'),
    path('carrucel/<int:id>/delete/', views.carrucel_delete, name='carrucel_delete'),

    path('procesar-pago/', views.procesar_pago, name='pago'),
    path('pago-nuevas/', views.agregar_pago, name='pago-nuevas'),
    path('pago-editar/<int:id>/modificar/', views.editar_pago, name='pago_editar'),
    path('pago-eliminar/<int:id>', views.eliminar_pago, name='pago_eliminar'),
    path('administrar-pedidos/', views.administrar_pedidos, name='administrar_pedidos'),
    path('ver-pedido/<int:pedido_id>/', views.VerPedidoView.as_view(), name='ver_pedido'),
    path('modificar-pedido/<int:pedido_id>/', views.ModificarPedidoView.as_view(), name='modificar_pedido'),
]

