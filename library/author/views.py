from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Author
from book.models import Book

def is_librarian(user):
    return user.is_authenticated and user.role == 'librarian'

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

@login_required
@user_passes_test(is_librarian)
def author_list_view(request):
    """
    Display a paginated list of authors with search functionality.
    Only accessible by librarians.
    """
    search_query = request.GET.get('q', '').strip()
    
    # Start with base queryset
    authors = Author.objects.all().prefetch_related('books')
    
    # Apply search if query exists
    if search_query:
        authors = authors.filter(
            Q(name__icontains=search_query) |
            Q(surname__icontains=search_query) |
            Q(patronymic__icontains=search_query)
        ).distinct()
    
    # Order by surname and name
    authors = authors.order_by('surname', 'name')
    
    # Pagination - 15 items per page
    paginator = Paginator(authors, 15)
    page = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Calculate the starting index for the current page
    start_index = (page_obj.number - 1) * paginator.per_page + 1
    
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
        'authors': page_obj.object_list,  # For backward compatibility
        'start_index': start_index,
    }
    
    # If this is an AJAX request, return a JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'html': render_to_string('author/includes/author_table.html', context, request=request),
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page_number': page_obj.number,
            'num_pages': paginator.num_pages,
            'count': paginator.count,
        }
        return JsonResponse(data)
    
    return render(request, 'author/author_list.html', context)

@login_required
@user_passes_test(is_librarian)
def author_create_view(request):
    """
    Handle creation of a new author with validation.
    Only accessible by librarians.
    """
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()
        patronymic = request.POST.get('patronymic', '').strip()
        
        # Validation flags
        has_errors = False
        
        # Validate name (only letters, spaces, and hyphens)
        if not name or not name.replace(' ', '').replace('-', '').isalpha():
            messages.error(request, 'Please enter a valid first name (letters, spaces, and hyphens only).')
            has_errors = True
        
        # Validate surname (only letters, spaces, and hyphens)
        if not surname or not surname.replace(' ', '').replace('-', '').isalpha():
            messages.error(request, 'Please enter a valid last name (letters, spaces, and hyphens only).')
            has_errors = True
        
        # Validate patronymic if provided (only letters, spaces, and hyphens)
        if patronymic and not patronymic.replace(' ', '').replace('-', '').isalpha():
            messages.error(request, 'Patronymic can only contain letters, spaces, and hyphens.')
            has_errors = True
        
        # Check for existing author with the same name
        if not has_errors and Author.objects.filter(
            name__iexact=name, 
            surname__iexact=surname,
            patronymic__iexact=patronymic if patronymic else ''
        ).exists():
            messages.warning(request, f'An author with the name {name} {surname} already exists.')
            has_errors = True
        
        if has_errors:
            return render(request, 'author/author_create.html', {
                'name': name,
                'surname': surname,
                'patronymic': patronymic,
            })
        
        try:
            # Create the author
            author = Author.objects.create(
                name=name.title(),
                surname=surname.title(),
                patronymic=patronymic.title() if patronymic else ''
            )
            
            messages.success(
                request, 
                f'Author {author.get_full_name()} has been successfully added.', 
                extra_tags='success'
            )
            
            # Redirect to the new author's detail page or back to the list
            if 'save_and_add_another' in request.POST:
                return redirect('author:author_create')
            elif 'save_and_edit' in request.POST:
                return redirect('author:author_edit', author_id=author.id)
            else:
                return redirect('author:author_list')
                
        except Exception as e:
            messages.error(
                request, 
                f'An error occurred while creating the author: {str(e)}',
                extra_tags='danger'
            )
            return render(request, 'author/author_create.html', {
                'name': name,
                'surname': surname,
                'patronymic': patronymic,
            })
    
    # GET request - show empty form
    return render(request, 'author/author_create.html')

@login_required
@user_passes_test(is_librarian)
def author_detail_view(request, author_id):
    """
    Display detailed information about a specific author and their books.
    Only accessible by librarians.
    """
    try:
        author = get_object_or_404(Author, id=author_id)
        
        # Get all books by this author with pagination
        books_list = author.books.all().order_by('title')
        
        # Pagination
        paginator = Paginator(books_list, 10)  # Show 10 books per page
        page_number = request.GET.get('page')
        books = paginator.get_page(page_number)
        
        context = {
            'author': author,
            'books': books,
            'books_count': books_list.count(),
        }
        
        return render(request, 'author/author_detail.html', context)
        
    except Exception as e:
        messages.error(
            request, 
            f'Error retrieving author details: {str(e)}',
            extra_tags='danger'
        )
        return redirect('author:author_list')


@login_required
@user_passes_test(is_librarian)
def author_edit_view(request, author_id):
    """
    Handle editing of an existing author.
    Only accessible by librarians.
    """
    author = get_object_or_404(Author, id=author_id)
    
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()
        patronymic = request.POST.get('patronymic', '').strip()
        
        # Validation flags
        has_errors = False
        
        # Validate name (only letters, spaces, and hyphens)
        if not name or not name.replace(' ', '').replace('-', '').isalpha():
            messages.error(request, 'Please enter a valid first name (letters, spaces, and hyphens only).')
            has_errors = True
        
        # Validate surname (only letters, spaces, and hyphens)
        if not surname or not surname.replace(' ', '').replace('-', '').isalpha():
            messages.error(request, 'Please enter a valid last name (letters, spaces, and hyphens only).')
            has_errors = True
        
        # Validate patronymic if provided (only letters, spaces, and hyphens)
        if patronymic and not patronymic.replace(' ', '').replace('-', '').isalpha():
            messages.error(request, 'Patronymic can only contain letters, spaces, and hyphens.')
            has_errors = True
        
        # Check for existing author with the same name (excluding current author)
        existing_author = Author.objects.filter(
            name__iexact=name, 
            surname__iexact=surname,
            patronymic__iexact=patronymic if patronymic else ''
        ).exclude(id=author_id).first()
        
        if existing_author:
            messages.warning(request, f'Another author with the name {name} {surname} already exists.')
            has_errors = True
        
        if has_errors:
            return render(request, 'author/author_edit.html', {
                'author': author,
                'name': name,
                'surname': surname,
                'patronymic': patronymic,
            })
        
        try:
            # Update the author
            author.name = name.title()
            author.surname = surname.title()
            author.patronymic = patronymic.title() if patronymic else ''
            author.save()
            
            messages.success(
                request, 
                f'Author {author.get_full_name()} has been successfully updated.',
                extra_tags='success'
            )
            
            # Redirect based on button clicked
            if 'save_and_continue' in request.POST:
                return redirect('author:author_edit', author_id=author.id)
            else:
                return redirect('author:author_list')
                
        except Exception as e:
            messages.error(
                request, 
                f'An error occurred while updating the author: {str(e)}',
                extra_tags='danger'
            )
            return render(request, 'author/author_edit.html', {
                'author': author,
                'name': name,
                'surname': surname,
                'patronymic': patronymic,
            })
    
    # GET request - show form with current data
    return render(request, 'author/author_edit.html', {
        'author': author,
        'name': author.name,
        'surname': author.surname,
        'patronymic': author.patronymic or '',
    })

@login_required
@user_passes_test(is_librarian)
@require_http_methods(["POST"])
def author_delete_view(request, author_id):
    """Handle deletion of an author if they have no books."""
    author = get_object_or_404(Author, pk=author_id)
    
    if author.books.exists():
        messages.error(request, 'Cannot delete author with books attached.')
    else:
        try:
            author_name = f"{author.name} {author.surname}"
            author.delete()
            messages.success(request, f'Author {author_name} has been deleted.')
        except Exception as e:
            messages.error(request, f'Error deleting author: {str(e)}')
    
    # Return to the previous page or author list
    return redirect(request.META.get('HTTP_REFERER', 'author:author_list'))


@login_required
@user_passes_test(is_librarian)
@csrf_exempt  # Only for demo - in production, use proper CSRF handling
@require_http_methods(["POST"])
def author_quick_add(request):
    """API endpoint for quick adding authors via AJAX."""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    name = request.POST.get('name', '').strip()
    surname = request.POST.get('surname', '').strip()
    
    if not name or not surname:
        return JsonResponse({'error': 'Name and surname are required'}, status=400)
    
    try:
        author = Author.objects.create(
            name=name,
            surname=surname,
            patronymic=request.POST.get('patronymic', '').strip()
        )
        return JsonResponse({
            'id': author.id,
            'name': f"{author.name} {author.surname}",
            'full_name': f"{author.name} {author.patronymic} {author.surname}".strip()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
