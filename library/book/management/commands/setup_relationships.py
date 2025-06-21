from django.core.management.base import BaseCommand
from book.models import Book
from django.db import connection

class Command(BaseCommand):
    help = 'Set up book-author relationships'

    def handle(self, *args, **options):
        # First, ensure the many-to-many table exists
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS author_author_books (
                        id SERIAL PRIMARY KEY,
                        author_id INTEGER NOT NULL,
                        book_id INTEGER NOT NULL,
                        CONSTRAINT author_author_books_author_id_book_id_uniq UNIQUE (author_id, book_id)
                    )
                """)
                self.stdout.write(self.style.SUCCESS('Created author_author_books table'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Note: {str(e)}'))
        
        # Set up relationships
        try:
            # Book 1: 1984 by George Orwell (ID: 1)
            book = Book.objects.get(pk=1)
            book.authors.add(1)
            
            # Book 2: Animal Farm by George Orwell (ID: 1)
            book = Book.objects.get(pk=2)
            book.authors.add(1)
            
            # Book 3: The Lord of the Rings by J.R.R. Tolkien (ID: 2)
            book = Book.objects.get(pk=3)
            book.authors.add(2)
            
            # Book 4: The Hobbit by J.R.R. Tolkien (ID: 2)
            book = Book.objects.get(pk=4)
            book.authors.add(2)
            
            # Book 5: To Kill a Mockingbird by Harper Lee (ID: 3)
            book = Book.objects.get(pk=5)
            book.authors.add(3)
            
            # Book 6: The Great Gatsby by F. Scott Fitzgerald (ID: 4)
            book = Book.objects.get(pk=6)
            book.authors.add(4)
            
            # Book 7: The Silmarillion by J.R.R. Tolkien (ID: 2)
            book = Book.objects.get(pk=7)
            book.authors.add(2)
            
            self.stdout.write(self.style.SUCCESS('Successfully set up book-author relationships'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting up relationships: {str(e)}'))
