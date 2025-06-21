from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Author
from .forms import AuthorForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Author

def is_librarian(user):
    return user.is_authenticated and getattr(user, 'role', '') == 'librarian'

@login_required
@user_passes_test(is_librarian)
def author_list_view(request):
    search_query = request.GET.get('q', '').strip()
    authors = Author.objects.all().prefetch_related('books')
    if search_query:
        authors = authors.filter(
            Q(name__icontains=search_query) |
            Q(surname__icontains=search_query) |
            Q(patronymic__icontains=search_query)
        ).distinct()
    authors = authors.order_by('surname', 'name')
    paginator = Paginator(authors, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_index = (page_obj.number - 1) * paginator.per_page + 1
    context = {
        'page_obj': page_obj,
        'start_index': start_index,
        'search_query': search_query,
    }
    return render(request, 'author/author_list.html', context)

@login_required
@user_passes_test(is_librarian)
def author_create_view(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'Author {author.name} {author.surname} added successfully.')
            if 'save_and_add_another' in request.POST:
                return redirect('author:author_create')
            elif 'save_and_edit' in request.POST:
                return redirect('author:author_edit', author_id=author.id)
            else:
                return redirect('author:author_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthorForm()
    return render(request, 'author/author_form.html', {'form': form, 'action': 'Add'})

@login_required
@user_passes_test(is_librarian)
def author_edit_view(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            # Унікальність з виключенням поточного автора
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            patronymic = form.cleaned_data.get('patronymic', '')
            exists = Author.objects.filter(name__iexact=name, surname__iexact=surname, patronymic__iexact=patronymic).exclude(id=author.id).exists()
            if exists:
                form.add_error(None, 'Another author with this full name already exists.')
            else:
                form.save()
                messages.success(request, f'Author {author.name} {author.surname} updated successfully.')
                if 'save_and_continue' in request.POST:
                    return redirect('author:author_edit', author_id=author.id)
                else:
                    return redirect('author:author_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthorForm(instance=author)
    return render(request, 'author/author_form.html', {'form': form, 'action': 'Edit', 'author': author})

@login_required
@user_passes_test(is_librarian)
def author_delete_view(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    if author.books.exists():
        messages.error(request, 'Cannot delete author with books attached.')
    else:
        author.delete()
        messages.success(request, f'Author {author.name} {author.surname} deleted successfully.')
    return redirect('author:author_list')

def author_detail_view(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    return render(request, 'author/author_detail.html', {'author': author})

@csrf_exempt  # лише для демонстрації — у продакшн краще налаштувати CSRF захист
def author_quick_add(request):
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=405)

    name = request.POST.get('name', '').strip()
    surname = request.POST.get('surname', '').strip()
    patronymic = request.POST.get('patronymic', '').strip()

    if not name or not surname:
        return JsonResponse({'error': 'Name and surname are required'}, status=400)

    try:
        author = Author.objects.create(name=name, surname=surname, patronymic=patronymic)
        return JsonResponse({
            'id': author.id,
            'name': f"{author.name} {author.surname}",
            'full_name': f"{author.name} {author.patronymic} {author.surname}".strip()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)