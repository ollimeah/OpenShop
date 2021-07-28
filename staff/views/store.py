from staff.models import FAQ
from django.views import generic
from django.urls import reverse

class FAQListView(generic.ListView):
    model = FAQ
    context_object_name = 'faqs'
    template_name = 'faqs/index.html'

class FAQDetailView(generic.DetailView):
    model = FAQ
    template_name = 'faqs/detail.html'

class FAQCreateView(generic.edit.CreateView):
    model = FAQ
    fields = '__all__'
    template_name = 'faqs/new.html'

    def get_success_url(self):
        return reverse('staff-faq', kwargs={'pk' : self.object.id})

class FAQUpdateView(generic.UpdateView):
    model = FAQ
    fields = '__all__'
    template_name = 'faqs/update.html'

    def get_success_url(self):
        return reverse('staff-faq', kwargs={'pk' : self.object.id})

class FAQDeleteView(generic.DeleteView):
    model = FAQ
    template_name = 'faqs/delete.html'

    def get_success_url(self):
        return reverse('staff-faqs')