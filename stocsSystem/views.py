from django.shortcuts import render, redirect
from .models import *
from .forms import StockCreateForm, StockSearchForm,StockUpdateForm
from .forms import IssueForm, ReceiveForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.
def home(request):
	title = 'Merhabalar Hocam Hoşgeldiniz :)'
	context = {
	"title": title,
	}
	return redirect('/list_item')

def list_item(request):
	header = 'MALZEME LİSTESİ'
	form = StockSearchForm(request.POST or None)
	queryset = Stock.objects.all()
	context = {
		"header": header,
		"queryset": queryset,
		"form": form,
	}
	if request.method == 'POST':
		queryset = Stock.objects.filter(category=form['category'].value(),
										item_name=form['item_name'].value()
										)
		context = {
			"form": form,
			"header": header,
			"queryset": queryset,
	}
	return render(request, "list_item.html", context)

def add_items(request):
	form = StockCreateForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('/list_item')
	context = {
		"form": form,
		"title": "MALZEME EKLE",
	}
	return render(request, "add_items.html", context)

def update_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = StockUpdateForm(instance=queryset)
	if request.method == 'POST':
		form = StockUpdateForm(request.POST, instance=queryset)
		if form.is_valid():
			form.save()
			return redirect('/list_item')

	context = {
		'form':form
	}
	return render(request, 'add_items.html', context)

def delete_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	if request.method == 'POST':
		queryset.delete()
		return redirect('/list_item')
	return render(request, 'delete_items.html')

def stock_detail(request, pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		"title": queryset.item_name,
		"queryset": queryset,
	}
	return render(request, "stock_detail.html", context)

def issue_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = IssueForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		#instance.receive_quantity=0
		instance.quantity -= instance.issue_quantity
		instance.issue_by = str(request.user)
		instance.save()
		issue_history = StockHistory(
			id=instance.id,
			last_updated=instance.last_updated,
			category_id=instance.category_id,
			item_name=instance.item_name,
			quantity=instance.quantity,
			issue_to=instance.issue_to,
			issue_by=instance.issue_by,
			issue_quantity=instance.issue_quantity,
		)
		issue_history.save()

		return redirect('/stock_detail/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())

	context = {
		"title": 'ÇIKIŞ ' + str(queryset.item_name),
		"queryset": queryset,
		"form": form,
		"username": 'ÇIKIŞ YAPAN KİŞİ: ' + str(request.user),
	}
	return render(request, "add_items.html", context)



def receive_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReceiveForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		#instance.issue_quantity = 0
		instance.quantity += instance.receive_quantity
		instance.save()
		receive_history = StockHistory(
			id=instance.id,
			last_updated=instance.last_updated,
			category_id=instance.category_id,
			item_name=instance.item_name,
			quantity=instance.quantity,
			receive_quantity=instance.receive_quantity,
			receive_by=instance.receive_by
		)
		receive_history.save()


		return redirect('/stock_detail/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())
	context = {
			"title": 'TESLİM ' + str(queryset.item_name),
			"instance": queryset,
			"form": form,
			"username": 'TESLİM EDEN: ' + str(request.user),
		}
	return render(request, "add_items.html", context)



@login_required
def list_history(request):
	header = 'MALZEME LİSTESİ ESKİ KAYITLARI'
	queryset = StockHistory.objects.all()
	context = {
		"header": header,
		"queryset": queryset,
	}
	return render(request, "list_history.html",context)



