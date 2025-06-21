from book.models import Book
from author.models import Author

def setup_relationships():
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

if __name__ == "__main__":
    setup_relationships()
