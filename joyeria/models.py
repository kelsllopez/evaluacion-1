from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from ckeditor.fields import RichTextField 
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator


# categorias
class Categoria(models.Model):
    nombre = models.CharField(max_length=30,unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='Categorias/%Y/%m/%d',blank=True)

    def __str__(self):
            return self.nombre
    
class Material(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
#Producto
class Productos(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True)
    Nombre = models.CharField(max_length=500, unique=True)
    Descripcion = RichTextField()
    Imagen = models.ImageField(upload_to='Productos/%Y/%m/%d', blank=True)
    Imagen2 = models.ImageField(upload_to='Productos/%Y/%m/%d', blank=True)
    Imagen3 = models.ImageField(upload_to='Productos/%Y/%m/%d', blank=True)
    Imagen_Central = models.ImageField(upload_to='Productos/%Y/%m/%d', blank=True)
    precio = models.IntegerField()
    stock = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    sexo = models.CharField(max_length=20, choices=(('mujer', 'Mujer'), ('hombre', 'Hombre')), default='mujer')


    def __str__(self):
        return self.Nombre
    
#Comentarios y Valoracion
class Comentarios(models.Model):
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Asociar el comentario con el usuario
    comentario = models.TextField()
    rating = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comentario
    
#carro de compras
class Carro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    producto_cantidad = models.IntegerField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return self.producto_cantidad * self.producto.precio

    @property
    def iva(self):
        return self.subtotal * 0.19

    @property
    def total_neto(self):
        return self.subtotal + self.iva


class DireccionEnvio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=12)
    rut = models.CharField(max_length=12)
    direccion = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=(('casa', 'Casa'), ('departamento', 'Departamento')))
    numero = models.CharField(max_length=10)
    predeterminada = models.BooleanField(default=False, help_text='Establecer como dirección de envío predeterminada')
    def __str__(self):
        return f'Dirección de {self.nombre_contacto} para {self.user.username}'


class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    mensaje = models.TextField()

    def __str__(self):
        return self.nombre
    class Meta:
        db_table = 'contacto'
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
        ordering = ['nombre']



class Pagos(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    numero_tarjeta = models.CharField(max_length=16, validators=[RegexValidator(r'^\d{16}$', 'Ingrese 16 dígitos válidos.')])
    valido_hasta = models.CharField(max_length=5, validators=[RegexValidator(r'^(0[1-9]|1[0-2])/\d{2}$', 'Ingrese una fecha válida en el formato MM/YY.')])
    numero_asociado = models.CharField(max_length=3, validators=[RegexValidator(r'^\d{3}$', 'Ingrese 3 dígitos válidos.')])

    def __str__(self):
        return f'Numero  de tarjeta  {self.numero_tarjeta} Valido hasta  {self.valido_hasta} numero Asociado {self.numero_asociado}'

import random
import string
def generate_order_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
class Pedidos(models.Model):
    ESTADOS_PEDIDO = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('En Camino', 'En Camino'),
        ('Entregado', 'Entregado'),
    ]
    direccion_envio = models.ForeignKey(DireccionEnvio, on_delete=models.CASCADE, default='your_default_value')
    metodo_pago = models.ForeignKey(Pagos, on_delete=models.CASCADE, default='your_default_value')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='Pendiente')
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pedido #{self.id} de {self.usuario.username} - Estado: {self.estado}'

    class Meta:
        db_table = 'pedidos'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-creado']
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedidos, on_delete=models.CASCADE)
    producto = models.ForeignKey(Productos, on_delete=models.SET_NULL, null=True)  # Cambiado a SET_NULL
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Detalle del Pedido #{self.pedido.id}'

    class Meta:
        db_table = 'detalle_pedidos'
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
#Comentarios y Valoracion
class Comentarios(models.Model):
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Asociar el comentario con el usuario
    comentario = models.TextField()
    rating = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comentario    

class Carrucel(models.Model):
    titulo = models.CharField(max_length=20)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='carucel')

class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    mensaje = models.TextField()

    def __str__(self):
        return self.nombre
    class Meta:
        db_table = 'contacto'
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
        ordering = ['nombre']

class PerfilCliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='perfil_fotos/', blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True, help_text='Formato: DD/MM/AAAA')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True, null=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'
