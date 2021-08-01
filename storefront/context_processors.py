from staff.models import Category, Collection

def categories(request):
    return {'categories': Category.get_visible()}

def collections(request):
    return {'collections': Collection.get_visible()}