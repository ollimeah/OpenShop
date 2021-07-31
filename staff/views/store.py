from staff.models import FAQ, Promotion
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

class PromotionListView(generic.ListView):
    model = Promotion
    context_object_name = 'promotions'
    template_name = 'promotions/index.html'

class PromotionDetailView(generic.DetailView):
    model = Promotion
    template_name = 'promotions/detail.html'
    slug_field = 'code'
    slug_url_kwarg = 'code'

class PromotionCreateView(generic.edit.CreateView):
    model = Promotion
    fields = '__all__'
    template_name = 'promotions/new.html'

    def get_success_url(self):
        return reverse('staff-promotion', kwargs={'code' : self.object.code})

class PromotionUpdateView(generic.UpdateView):
    model = Promotion
    fields = '__all__'
    slug_field = 'code'
    slug_url_kwarg = 'code'
    template_name = 'promotions/update.html'

    def get_success_url(self):
        return reverse('staff-promotion', kwargs={'code' : self.object.code})

class PromotionDeleteView(generic.DeleteView):
    model = Promotion
    template_name = 'promotions/delete.html'
    slug_field = 'code'
    slug_url_kwarg = 'code'

    def get_success_url(self):
        return reverse('staff-promotions')