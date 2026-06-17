from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Client


@login_required
def client_list(request):
    clients = Client.objects.all().order_by('-created_at')
    return render(request, 'clients/list.html', {'clients': clients})


@login_required
def client_new(request):
    if request.method == 'POST':
        Client.objects.create(
            company_name=request.POST.get('company_name'),
            contact_person=request.POST.get('contact_person'),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            industry=request.POST.get('industry', ''),
            notes=request.POST.get('notes', ''),
        )
        return redirect('clients:list')
    return render(request, 'clients/new.html')


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'clients/detail.html', {'client': client})
