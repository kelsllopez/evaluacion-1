from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, ExpressionWrapper, fields
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
IVA_PERCENTAGE = 0.19
from django.http import Http404
from django.db.models import Count

#INICIO


def index(request):
    productos = Productos.objects.all().order_by('id')
    paginator = Paginator(productos, 12)
    carrusel = Carrucel.objects.all()
    ca = Categoria.objects.exclude(imagen='')

    page = request.GET.get('page')
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)

    query = request.GET.get('q')
    if query:
        productos = Productos.objects.filter(Q(Nombre__icontains=query))

    return render(request, 'iindex.html', {'productos': productos, 'mostrar_mapa': True, 'carrusel': carrusel, 'ca': ca})

#PRODCUTOS CATEGORIAS

def productoxCategoria(request, nombre):  
    nombre_categoria = nombre.replace('-', ' ')
    categoria = get_object_or_404(Categoria, nombre=nombre_categoria)
    productos = Productos.objects.filter(categoria=categoria)
    filtro_form = FiltroProductosForm(request.GET)
    
    if filtro_form.is_valid():
        material = filtro_form.cleaned_data.get('material')
        precio_min = filtro_form.cleaned_data.get('precio_min')
        precio_max = filtro_form.cleaned_data.get('precio_max')
        sexo = filtro_form.cleaned_data.get('sexo')  

        if material and material != '':
            productos = productos.filter(material__nombre=material)
            productos = productos.exclude(material__nombre='') if material == '' else productos.filter(material__nombre=material)
        
        if precio_min is not None:
            productos = productos.filter(precio__gte=precio_min)
        
        if precio_max is not None:
            productos = productos.filter(precio__lte=precio_max)

        if sexo and sexo != '':
            productos = productos.filter(sexo=sexo)
    
    data = {
        'productos': productos,
        'filtro_form': filtro_form,
        'categoria': categoria,  
    }
    return render(request, 'iindex.html', data)

#PRODUCTOS

def detalleProducto(request, nombre):  # Cambia de slug a nombre
    nombre_producto = nombre.replace('-', ' ')
    producto = get_object_or_404(Productos, Nombre=nombre_producto)
    productosRelacionados = Productos.objects.filter(categoria=producto.categoria)
    comentarios = Comentarios.objects.filter(producto=producto)

    nuevo_comentario_id = None  # Inicialmente no hay comentario nuevo
    mostrar_mas_comentarios = False  # Variable para controlar si se muestran más comentarios

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.producto = producto

            if request.user.is_authenticated:
                comentario.usuario = request.user  # Asocia el comentario con el usuario autenticado
            else:
                # Asocia el comentario con un usuario anónimo (puedes ajustar esto según tus necesidades)
                comentario.usuario = None  

            comentario.save()
            nuevo_comentario_id = comentario.id  # Guarda el ID del comentario recién ingresado
    else:
        form = ComentarioForm()


    # Si se ha enviado una solicitud para mostrar más comentarios
    if 'mostrar_mas' in request.GET:
        mostrar_mas_comentarios = True

    # Modifica la consulta para incluir solo los comentarios del producto actual y asociados al usuario autenticado

    # Agrega una consulta para contar la cantidad de personas que eligieron cada estrella
    conteo_estrellas = Comentarios.objects.filter(producto=producto).values('rating').annotate(count=Count('rating'))

    data = {
        'productos': producto,
        'productosRelacionados': productosRelacionados,
        'comentarios': comentarios,  # Ahora solo incluye los comentarios del usuario autenticado
        'form': form,
        'nuevo_comentario_id': nuevo_comentario_id,  # Pasa el ID del comentario al contexto
        'mostrar_mas_comentarios': mostrar_mas_comentarios,  # Pasa la variable de control al contexto
        'conteo_estrellas': conteo_estrellas,  # Pasa el conteo de estrellas al contexto
    }

    return render(request, 'productos/detalle.html', data)

def listar_productos(request):
    productoss = Productos.objects.all()
    title = "Listado de Productos"  # Set the title here
    query = request.GET.get('q')
    if query:
        productoss = productoss.filter(Q(Nombre__icontains=query))
    return render(request, 'productos/listar.html', {'productoss': productoss, 'title': title})

def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto agregado correctamente.")
            return redirect('/listar-productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/agregar.html', {'form': form})

def eliminar_producto(request, nombre):
    producto = get_object_or_404(Productos, Nombre=nombre)

    producto.delete()

    # Mensaje de éxito
    messages.success(request, "Producto eliminado correctamente.")

    # Redirige a la lista de productos
    return redirect('/listar-productos')

def modificar_producto(request, nombre):  # Cambia de slug a nombre
    productos = get_object_or_404(Productos, Nombre=nombre)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=productos)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto modificado correctamente.")
            return redirect('/listar-productos', Nombre=productos.Nombre)
    else:
        form = ProductoForm(instance=productos)
    return render(request, 'productos/modificar.html', {'form': form, 'productos': productos})


#panel
def panel(request):
    customercount=User.objects.all().count()
    productcount=Productos.objects.all().count()
    materialcount=Material.objects.all().count()
    categoriacount=Categoria.objects.all().count()
    comentariocount=Comentarios.objects.all().count()
    contactocount=Contacto.objects.all().count()
    return render(request, 'panel/index.html', {  'customercount':customercount,'productcount':productcount,'materialcount':materialcount,'categoriacount':categoriacount,'comentariocount':comentariocount,'contactocount':contactocount})


def perfil_de_usuario(request):
    # Lógica para la vista de Perfil de Usuario
    return render(request, 'panel/perfil_de_usuario.html')

#MATERIAL

def mostrar_materiales(request):
    # Lógica para la vista de Materiales
    materiales = Material.objects.all()

    # Búsqueda de materiales
    query = request.GET.get('q')
    if query:
        materiales = materiales.filter(Q(nombre__icontains=query))

    return render(request, 'panel/material/mostrar_materiales.html', {'materiales': materiales})

def agregar_material(request):
    # Lógica para agregar un nuevo material
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Material  Agregado correctamente")

            return redirect('tienda:mostrar_materiales')
    else:
        form = MaterialForm()

    return render(request, 'panel/material/agregar_material.html', {'form': form})

def editar_material(request, material_id):
    # Lógica para editar un material existente
    material = get_object_or_404(Material, id=material_id)

    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, "Material  modificado correctamente")
            return redirect('tienda:mostrar_materiales')
    else:
        form = MaterialForm(instance=material)

    return render(request, 'panel/material/editar_material.html', {'form': form, 'material': material})

def eliminar_material(request, material_id):
    # Lógica para eliminar un material
    material = get_object_or_404(Material, id=material_id)
    
    if request.method == 'POST':
        material.delete()
        messages.success(request, "Material  Eliminado correctamente")

        return redirect('tienda:mostrar_materiales')

    return render(request, 'panel/material/eliminar_material.html', {'material': material})

#COMENTARIO

def listar_comentarios(request):
    comentarios = Comentarios.objects.all()
    return render(request, 'panel/comentarios/listar_comentarios.html', {'comentarios': comentarios})


def eliminar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentarios, id=comentario_id)
    
    if request.method == 'POST':
        comentario.delete()
        messages.success(request, f"Comentario Eliminado Exitosamente")
        return redirect('tienda:listar_comentarios')

    return render(request, 'panel/comentarios/eliminar_comentario.html', {'comentario': comentario})
#Categoria

def ListarCategorias(request):
    categorias = Categoria.objects.all()

    query = request.GET.get('q')

    if query:
        categorias = categorias.filter(Q(nombre__icontains=query))
        query = request.GET.get('q')

    return render(request, 'categorias/listar.html', {'categorias': categorias})

def AgregarCategoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría agregada correctamente.")
            return redirect('tienda:listar_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'categorias/agregar.html', {'form': form})

def ModificarCategoria(request, nombre):  # Cambia de slug a nombre
    categoria = get_object_or_404(Categoria, nombre=nombre)
    data = {
        'form': CategoriaForm(instance=categoria)
    }
    if request.method == 'POST':
        formulario = CategoriaForm(data=request.POST, instance=categoria)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Categoria  modificada correctamente")
            return redirect('tienda:listar_categorias')
        else:
            data["form"] = formulario

    return render(request, 'categorias/modificar.html', data)

def eliminar_categorias(request, nombre):  # Cambia de slug a nombre
    categoria = get_object_or_404(Categoria, nombre=nombre)
    productos = Productos.objects.filter(categoria=categoria)
    productos.delete()
    categoria.delete()
    messages.success(request, "Categoría eliminada correctamente.")
    return redirect('tienda:listar_categorias')
#REGISTRO Y INICIO SESION

def registro(request):
    data = {
        'form': RegistroForm()
    }

    if request.method == 'POST':
        formulario = RegistroForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            user = authenticate(username=formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            login(request, user)
            messages.success(request, 'Usuario registrado correctamente')
            return redirect('/')
        else:
            data['form'] = formulario
    
    return render(request, 'auth/registrar.html', data)

    
def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido, {request.user.username}!")

            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/iniciar_sesion.html', {'form': form})
@login_required
def add_to_cart(request, producto_id):
    producto = get_object_or_404(Productos, id=producto_id)
    user = request.user

    if request.method == 'POST':
        cantidad = int(request.POST['qty'])

        if cantidad <= 0:
            messages.error(request, "La cantidad debe ser mayor que 0.")
        else:
            with transaction.atomic():
                carro_item, created = Carro.objects.get_or_create(usuario=user, producto=producto, defaults={'producto_cantidad': 0})

                if not created:
                    stock_disponible = producto.stock - carro_item.producto_cantidad

                    if stock_disponible < cantidad:
                        messages.error(request, "No hay suficiente stock disponible para esa cantidad.")
                        return redirect('tienda:cart')

                    Carro.objects.filter(usuario=user, producto=producto).update(producto_cantidad=F('producto_cantidad') + cantidad)
                else:
                    if producto.stock < cantidad:
                        messages.error(request, "No hay suficiente stock disponible para esa cantidad.")
                        return redirect('tienda:cart')

                    carro_item.producto_cantidad = cantidad
                    carro_item.save()

                # Obtener 'stock_temp' de la sesión y convertirlo a diccionario si es una cadena
                stock_temp_str = request.session.get('stock_temp', '{}')
                stock_temp = json.loads(stock_temp_str)

                stock_temp[producto_id] = producto.stock - carro_item.producto_cantidad

                # Serializar antes de almacenar en la sesión
                request.session['stock_temp'] = json.dumps(stock_temp, cls=DjangoJSONEncoder)
                request.session.modified = True

                messages.success(request, f"{cantidad} {producto.Nombre} ha sido agregado al carro.")

    return redirect('tienda:cart')

def cart_page(request):
    user = request.user
    carrito = Carro.objects.filter(usuario=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_items = request.POST.getlist('selected_items')
        
        if action == 'comprar':
            nuevo_pedido = Pedidos.objects.create(
                cuenta="1234567890123456",
                valida_hasta="2023-01-01",
                numero_asociado=123
            )
            # Obtén los elementos seleccionados del carrito
            items_seleccionados = Carro.objects.filter(usuario=user, id__in=selected_items)

            # Asocia los elementos del carrito al nuevo pedido
            nuevo_pedido.carrito.set(items_seleccionados)

            # Luego, puedes redirigir al usuario a la vista del pedido recién creado
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('tienda:pedido')



    context = {
        'carrito': carrito,
    }

    return render(request, 'carrito/carro_compras.html', context)

def eliminar_items_carrito(request):
    if request.method == 'POST':
        user = request.user
        selected_items = request.POST.getlist('selected_items')

        if selected_items:
            # Obtiene los elementos a eliminar antes de borrarlos
            items_a_eliminar = Carro.objects.filter(usuario=user, id__in=selected_items)

            # Elimina los elementos del carrito
            items_a_eliminar.delete()

            # Agrega un mensaje indicando que los elementos se eliminaron con éxito
            messages.success(request, f"Elementos del carrito eliminados exitosamente.")
        else:
            # Agrega un mensaje indicando que no se seleccionaron elementos para eliminar
            messages.warning(request, "No se seleccionaron elementos para eliminar.")

    # Redirige al usuario a la página del carrito
    return redirect('tienda:cart')

#PEDIDO
def procesar_pedido(request):
    user = request.user
    carrito = Carro.objects.filter(usuario=user)

    if request.method == 'POST':
        form = PedidoForm(request.POST)

        if form.is_valid():
            # Obtiene la dirección de envío y el método de pago seleccionados
            direccion_envio = form.cleaned_data['direccion_envio']
            metodo_pago = form.cleaned_data['metodo_pago']

            with transaction.atomic():
                # Ejemplo de creación de un nuevo pedido y detalles del pedido:
                nuevo_pedido = Pedidos.objects.create(
                    direccion_envio=direccion_envio,
                    metodo_pago=metodo_pago,
                    usuario=user,
                    total=0,  # Calcula el total real según tus necesidades
                    estado='Pendiente',
                )

                total_pedido = 0  # Inicializa el total del pedido

                detalles_pedido = []  # Lista para almacenar detalles del pedido

                for item in carrito:
                    detalle = DetallePedido.objects.create(
                        pedido=nuevo_pedido,
                        producto=item.producto,
                        cantidad=item.producto_cantidad,
                        subtotal=item.subtotal,
                    )

                    detalles_pedido.append(detalle)  # Agrega el detalle a la lista

                    # Actualiza el stock del producto
                    item.producto.stock -= item.producto_cantidad
                    item.producto.save()

                    total_pedido += item.subtotal  # Actualiza el total del pedido

                # Actualiza el total del pedido con el total calculado
                nuevo_pedido.total = total_pedido
                nuevo_pedido.save()

                # Limpia el carrito después de procesar el pedido
                carrito.delete()

                # Pasa los detalles del pedido al contexto
                context = {'detalles_pedido': detalles_pedido, 'pedido': nuevo_pedido}

                # Redirige al usuario a la página de lista de pedidos con los detalles
                return redirect('tienda:lista_pedidos')

    else:
        form = PedidoForm()

    # Actualiza las opciones del formulario con las direcciones de envío y métodos de pago del usuario
    form.fields['direccion_envio'].queryset = DireccionEnvio.objects.filter(user=user)
    form.fields['metodo_pago'].queryset = Pagos.objects.filter(user=user)

    context = {
        'carrito': carrito,
        'form': form,
    }

    return render(request, 'carrito/proceso_compra.html', context)





def lista_pedidos(request):
    pedidos = Pedidos.objects.filter(usuario=request.user).order_by('-creado')

    detalles_pedidos = []

    for pedido in pedidos:
        detalles_pedido = DetallePedido.objects.filter(pedido=pedido)

        # Filtra los detalles de pedido donde el producto aún existe o el campo producto es NULL
        detalles_pedido = [detalle for detalle in detalles_pedido if detalle.producto or detalle.producto_id is None]

        detalles_pedidos.append(detalles_pedido)

    return render(request, 'carrito/lista_pedidos.html', {'pedidos': zip(pedidos, detalles_pedidos)})


def administrar_pedidos(request):
    # Obtener todos los pedidos
    pedidos = Pedidos.objects.all()


    return render(request, 'carrito/administrador.html', {'pedidos': pedidos})

from django.views import View

class VerPedidoView(View):
    template_name = 'carrito/ver_pedido.html'

    def get(self, request, pedido_id):
        pedido = get_object_or_404(Pedidos, id=pedido_id)
        return render(request, self.template_name, {'pedido': pedido})


class ModificarPedidoView(View):
    template_name = 'carrito/modificar_pedido.html'

    def get(self, request, pedido_id, *args, **kwargs):
        pedido = get_object_or_404(Pedidos, id=pedido_id)
        form = ModificarPedidoForm(instance=pedido)
        return render(request, self.template_name, {'pedido': pedido, 'form': form})

    def post(self, request, pedido_id, *args, **kwargs):
        pedido = get_object_or_404(Pedidos, id=pedido_id)
        form = ModificarPedidoForm(request.POST, request.FILES, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, "Estado modificado correctamente.")
            return redirect('tienda:administrar_pedidos')  # Eliminé el uso de 'slug' ya que no estás utilizando ese campo
        return render(request, self.template_name, {'pedido': pedido, 'form': form})

#UBICACIONES

def ubicacion(request):
    # Obtén las direcciones de envío del usuario
    direcciones = DireccionEnvio.objects.filter(user=request.user)

    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            nueva_direccion = form.save(commit=False)
            nueva_direccion.user = request.user
            nueva_direccion.save()
            # Redirecciona para evitar envíos de formulario duplicados
            return redirect('tienda:ubicacion')
    else:
        form = DireccionEnvioForm()

    return render(request, 'perfil/datosenvio/ubicacion.html', {'form': form, 'direcciones': direcciones})

def ubicacion_nuevas(request):
    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            nueva_direccion = form.save(commit=False)
            nueva_direccion.user = request.user
            nueva_direccion.save()
            return redirect('tienda:ubicacion')  # Redirigir a la misma vista para agregar más ubicaciones
    else:
        form = DireccionEnvioForm()

    direcciones = DireccionEnvio.objects.filter(user=request.user)
    
    return render(request, 'perfil/datosenvio/ubicacion_nuevas.html', {'form': form, 'direcciones': direcciones})

def editar_ubicacion(request, id):
    ubicacion = DireccionEnvio.objects.get(id=id)

    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST, instance=ubicacion)
        if form.is_valid():
            form.save()
            return redirect('tienda:ubicacion')  # Redirige a la página de ubicaciones
    else:
        form = DireccionEnvioForm(instance=ubicacion)

    return render(request, 'perfil/datosenvio/editar_ubicacion.html', {'form': form})

def eliminar_ubicacion(request, id):
    ubicacion = DireccionEnvio.objects.get(id=id)
    ubicacion.delete()
    return redirect('tienda:ubicacion')  # Redirige a la página de ubicaciones

#PERFIL

def valoraciones(request):
    # Obtén todas las valoraciones del usuario actual
    valoraciones_usuario = Comentarios.objects.filter(usuario=request.user)
    return render(request, 'perfil/valoraciones.html', {'valoraciones_usuario': valoraciones_usuario})

def ajustes(request):
    # Lógica para la página de Ajustes
    return render(request, 'perfil/ajuste/ajustes.html')

#CONTACTO

def contacto(request):
    data = {
        'form': ConctactoForm()
    }

    if request.method == 'POST':
        formulario = ConctactoForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Gracias por su mensaje")
        else:
            data["form"] = formulario
    return render(request, 'panel/contacto/contacto.html', data)

def mostrar_contacto(request):
    contacto = Contacto.objects.all()
    query = request.GET.get('q')
    if query:
        contacto = contacto.filter(Q(nombre__icontains=query))
    m = {'contacto': contacto ,
        'title': 'MOSTRAR Contactos',
        }
    return render(request, 'panel/contacto/mostrar.html',m)

def detalle_contacto(request, id):
    contacto = get_object_or_404(Contacto, id=id)
    data = {
        'contacto': contacto,
    }
    return render(request, 'panel/contacto/detalle.html', data)

def eliminar_contacto(request, id):
    contacto = get_object_or_404(Contacto, id=id)
    contacto.delete()
    messages.success(request, "Mensaje de Contacto eliminado correctamente")
    return redirect(to="/listarcontacto")

#PERFIL USUARIO


def usuario_administrar(request):
    users = User.objects.all()
    busqueda = request.GET.get("buscador")
    paginator = Paginator(users, 9)
    page = request.GET.get('page', 1)

    if busqueda:
        users = User.objects.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        ).distinct()

        paginator = Paginator(users, 9)

    try:
        users_page = paginator.page(page)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except:
        raise Http404

    data = {
        'title': 'LISTADO DE PERSONAS INGRESADAS AL SISTEMA',
        'users': users_page,
    }

    return render(request, 'panel/usuario/adminusuario.html', data)

def usuario_administrar_eliminar (request, id):
    users = User.objects.get(id=id)
    users.delete()
    messages.success(request, 'Eliminado Correctamente al usuario')
    return redirect('/solgas/usuario/administrar/')

def crear_usuario(request):
    if request.method == 'POST':
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.create_user(email, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return redirect('/solgas/usuario/administrar/')
    return render(request, 'panel/usuario/crearusuario.html')

def usuario_administrar_modificar(request, id):
    user = User.objects.get(id=id)

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user.password = RegistroForm(password)  # Hash the password
            user.save()
            return redirect('tienda:usuarioadministrar')
    else:
        form = RegistroForm(initial={'id': id})

    data = {'form': form}
    return render(request, 'panel/usuario/usuariomodificar.html', data)

#CARUCEL

def carrucel_list(request):
    carruceles = Carrucel.objects.all()
    return render(request, 'panel/carrucel/list.html', {'carruceles': carruceles})

def carrucel_detail(request, id):
    carrucel = get_object_or_404(Carrucel, id=id)
    return render(request, 'panel/carrucel/detail.html', {'carrucel': carrucel})

def carrucel_create(request):
    if request.method == 'POST':
        titulo = request.POST['titulo']
        descripcion = request.POST['descripcion']
        imagen = request.FILES['imagen']
        carrucel = Carrucel(titulo=titulo, descripcion=descripcion, imagen=imagen)
        carrucel.save()
        messages.success(request, 'Carucel Agregado exitosamente.')

        return redirect('tienda:carrucel_list')
    return render(request, 'panel/carrucel/create.html')

def carrucel_update(request, id):
    carrucel = get_object_or_404(Carrucel, id=id)
    if request.method == 'POST':
        carrucel.titulo = request.POST['titulo']
        carrucel.descripcion = request.POST['descripcion']
        if 'imagen' in request.FILES:
            carrucel.imagen = request.FILES['imagen']
        carrucel.save()
        messages.success(request, 'Carucel actualizado exitosamente.')

        return redirect('tienda:carrucel_list')
    return render(request, 'panel/carrucel/update.html', {'carrucel': carrucel})

def carrucel_delete(request, id):
    carrucel = get_object_or_404(Carrucel, id=id)
    if request.method == 'POST':
        carrucel.delete()
        messages.success(request, 'Carucel Eliminado exitosamente.')

        return redirect('tienda:carrucel_list')
    return render(request, 'panel/carrucel/delete.html', {'carrucel': carrucel})

def procesar_pago(request):
    pagos = Pagos.objects.filter(user=request.user)

    if request.method == 'POST':
        form = PagosForm(request.POST)
        if form.is_valid():
            nueva_pago = form.save(commit=False)
            nueva_pago.user = request.user
            nueva_pago.save()
            messages.success(request, '¡Pago procesado correctamente!')
            return redirect('tienda:perfilpedido')
    else:
        form = PagosForm()

    return render(request, 'perfil/pago/procesar_pago.html', {'form': form, 'pagos': pagos})

def listar_pagos(request):
    pagos = Pagos.objects.all()
    return render(request, 'perfil/pago/listar_pagos.html', {'pagos': pagos})

def editar_pago(request, id):
    pago = Pagos.objects.get(id=id)

    if request.method == 'POST':
        form = PagosForm(request.POST, instance=pago)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Pago editado correctamente!')
            return redirect('tienda:pago')
    else:
        form = PagosForm(instance=pago)

    return render(request, 'perfil/pago/editar_pago.html', {'form': form, 'pago': pago})

def agregar_pago(request):
    if request.method == 'POST':
        form = PagosForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Pago agregado correctamente!')
            return redirect('tienda:pago')
    else:
        form = PagosForm()

    return render(request, 'perfil/pago/agregar_pago.html', {'form': form})

def eliminar_pago(request, id):
    pago = Pagos.objects.get(id=id)
    pago.delete()
    messages.success(request, '¡Pago eliminado correctamente!')
    return redirect('tienda:pago')

def ajustes(request):
    perfil, created = PerfilCliente.objects.get_or_create(user=request.user)
    return render(request, 'perfil/ajuste/ajustes.html', {'perfil': perfil})

from .forms import CustomUserChangeForm

@login_required
def editar_perfil(request, user_id):
    user = get_object_or_404(User, id=user_id)

    try:
        perfil = user.perfilcliente
    except PerfilCliente.DoesNotExist:
        perfil = None

    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=user)
        perfil_form = PerfilClienteForm(request.POST, request.FILES, instance=perfil)

        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()

            if perfil is None:
                perfil = PerfilCliente(user=user)

            perfil.foto = perfil_form.cleaned_data['foto']
            perfil.fecha_nacimiento = perfil_form.cleaned_data['fecha_nacimiento']
            perfil.telefono = perfil_form.cleaned_data['telefono']
            perfil.sexo = perfil_form.cleaned_data['sexo']

            perfil.save()

            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('tienda:editar_perfil', user_id=user.id)
    else:
        user_form = CustomUserChangeForm(instance=user)
        perfil_form = PerfilClienteForm(instance=perfil)

    return render(request, 'perfil/ajuste/editar.html', {'user_form': user_form, 'perfil_form': perfil_form, 'perfil': perfil})
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'perfil/ajuste/password_change.html'  
    success_url = reverse_lazy('tienda:ajustes')  

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Contraseña cambiada exitosamente.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error al cambiar la contraseña. Por favor, verifica los datos.')
        return super().form_invalid(form)