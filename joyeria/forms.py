from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Column, Field, ButtonHolder, Submit,HTML
from django.contrib.auth.forms import UserChangeForm
from django.forms import DateInput


#productos

class ProductoForm(forms.ModelForm):
    Descripcion = RichTextField()

    class Meta:
        model = Productos
        fields = "__all__"
        
    def clean(self):
        cleaned_data = super().clean()
        imagen = cleaned_data.get('Imagen')
        imagen2 = cleaned_data.get('Imagen2')
        imagen3 = cleaned_data.get('Imagen3')
        imagen_central = cleaned_data.get('Imagen_Central')

        if not imagen or not imagen2 or not imagen3 or not imagen_central:
            raise forms.ValidationError('Debe ingresar todas las imágenes.')

class FiltroProductosForm(forms.Form):
    material = forms.ModelChoiceField(queryset=Material.objects.all(), required=False, empty_label="Todos los materiales")
    precio_min = forms.IntegerField(min_value=0, required=False)
    precio_max = forms.IntegerField(min_value=0, required=False)
    sexo = forms.ChoiceField(choices=(('', 'Todos'), ('mujer', 'Mujer'), ('hombre', 'Hombre')), required=False, label='Sexo')

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'

class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegistroForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'email',
            'password1',
            'password2',
            Submit('submit', 'Registrarseuwu', css_class='btn btn-primary btn-lg')
        )
        # Agregar las clases de Bootstrap a los campos del formulario
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Correo electrónico'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})



class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentarios
        fields = [ 'comentario', 'rating']

class DireccionEnvioForm(forms.ModelForm):
    class Meta:
        model = DireccionEnvio
        fields = [
            'nombre_contacto',
            'telefono',
            'rut',
            'direccion',
            'tipo',
            'numero',
            'predeterminada',
        ]

        widgets = {
            'telefono': forms.TextInput(attrs={'placeholder': 'Ejemplo: (+56965604235)'}),
        }

    telefono = forms.CharField(
        max_length=12,
 
    )

    rut = forms.CharField(
        max_length=12,
    )

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['nombre']

class ConctactoForm(forms.ModelForm):

    class Meta:
        model = Contacto
        widgets={
            'mensaje': forms.Textarea(attrs={
                'rows':5,
                'cols':30
                }),
        }
        fields = '__all__'


class PagosForm(forms.ModelForm):
    class Meta:
        model = Pagos
        fields = ['numero_tarjeta', 'valido_hasta', 'numero_asociado']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Realizar Pagos'))
        
        # Personalizar el widget para el campo numero_tarjeta
        self.fields['numero_tarjeta'].widget = forms.TextInput(attrs={'placeholder': 'xxxx xxxx xxxx xxxx', 'title': 'Ingrese 16 dígitos válidos'})
        self.fields['numero_tarjeta'].validators = [RegexValidator(r'^\d{16}$', 'Ingrese 16 dígitos válidos.')]

        # Personalizar el widget para el campo valido_hasta
        self.fields['valido_hasta'].widget = forms.TextInput(attrs={'placeholder': 'MM/YY', 'title': 'Ingrese una fecha válida en el formato MM/YY'})
        self.fields['valido_hasta'].validators = [RegexValidator(r'^(0[1-9]|1[0-2])/\d{2}$', 'Ingrese una fecha válida en el formato MM/YY.')]

        self.fields['numero_asociado'].widget = forms.TextInput(attrs={'placeholder': 'xxx', 'title': 'Ingrese 3 dígitos válidos'})
        self.fields['numero_asociado'].validators = [RegexValidator(r'^\d{3}$', 'Ingrese 3 dígitos válidos.')]

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedidos
        fields = ['direccion_envio','metodo_pago']



class ModificarPedidoForm(forms.ModelForm):
    class Meta:
        model = Pedidos
        fields = ['estado']
        widgets = {'estado': forms.Select(attrs={'class': 'form-control'})}


class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = PerfilCliente
        fields = ['foto', 'fecha_nacimiento', 'telefono', 'sexo']
        widgets = {
            'fecha_nacimiento': DateInput(attrs={'type': 'date'}),
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email','first_name', 'last_name']
