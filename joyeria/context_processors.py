from .models import Categoria

def extras(request):
	lista_categorias = Categoria.objects.all()
	return {'categorias':lista_categorias}



	# total = total + int(value["precio"]*value["cantidad"])
