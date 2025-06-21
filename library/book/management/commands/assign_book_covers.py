import os
from django.core.management.base import BaseCommand
from django.core.files import File
from book.models import Book

class Command(BaseCommand):
    help = 'Assigns book covers from the book_covers directory to books based on their names'

    def handle(self, *args, **options):
        # Define the path to the book_covers directory
        covers_dir = 'media/book_covers'
        
        # Get all book cover filenames
        try:
            cover_files = os.listdir(covers_dir)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Directory {covers_dir} not found'))
            return
        
        self.stdout.write(f'Found {len(cover_files)} cover images in {covers_dir}')
        
        # Process each cover file
        for filename in cover_files:
            # Extract the book name from the filename (remove extension and replace underscores with spaces)
            book_name = os.path.splitext(filename)[0].replace('_', ' ').title()
            
            # Special case for "The Lord of the Rings"
            if 'lord ofthe rings' in book_name.lower():
                book_name = 'The Lord of the Rings'
            
            # Try to find a matching book
            try:
                # First try exact match
                book = Book.objects.get(name__iexact=book_name)
            except Book.DoesNotExist:
                # If no exact match, try partial match
                books = Book.objects.filter(name__icontains=book_name.split()[0])
                if books.exists():
                    book = books.first()
                    self.stdout.write(self.style.WARNING(
                        f'No exact match for "{book_name}", using "{book.name}"'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'No book found matching cover: {filename} (searched for "{book_name}")'
                    ))
                    continue
            except Book.MultipleObjectsReturned:
                self.stdout.write(self.style.WARNING(
                    f'Multiple books found for cover: {filename}, skipping'
                ))
                continue
            
            # Check if the book already has a cover
            if book.cover_image:
                self.stdout.write(f'Book "{book.name}" already has a cover, skipping')
                continue
            
            # Assign the cover
            cover_path = os.path.join(covers_dir, filename)
            with open(cover_path, 'rb') as f:
                book.cover_image.save(filename, File(f), save=True)
            
            self.stdout.write(self.style.SUCCESS(
                f'Assigned cover "{filename}" to book "{book.name}"'
            ))
        
        self.stdout.write(self.style.SUCCESS('Finished assigning book covers'))
