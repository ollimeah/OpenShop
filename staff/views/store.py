from staff.models import FAQ, Promotion, Delivery, CarouselImage
from django.views import generic
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from .views import staff_check
from django.contrib.auth.decorators import user_passes_test

class StaffTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Staff').exists()
    
    def get_login_url(self):
        return reverse('staff-login')

class FAQListView(StaffTestMixin, generic.ListView):
    model = FAQ
    context_object_name = 'faqs'
    template_name = 'faqs/index.html'

class FAQView(StaffTestMixin):
    model = FAQ
    fields = '__all__'
    template_name = 'faqs/view.html'

    def get_success_url(self):
        return reverse('staff-faqs')

class FAQCreateView(FAQView, generic.edit.CreateView): pass

class FAQUpdateView(FAQView, generic.UpdateView): pass

class FAQDeleteView(FAQView, generic.DeleteView):
    def get(self, request, pk):
        return redirect('staff-faqs')

class PromotionListView(StaffTestMixin, generic.ListView):
    model = Promotion
    context_object_name = 'promotions'
    template_name = 'promotions/index.html'

class PromotionDetailView(StaffTestMixin, generic.DetailView):
    model = Promotion
    template_name = 'promotions/detail.html'
    slug_field = 'code'
    slug_url_kwarg = 'code'

class PromotionCreateView(StaffTestMixin, generic.edit.CreateView):
    model = Promotion
    fields = ['code', 'max_uses', 'amount', 'min_spend', 'customer_limit', 'expiry', 'active']

    def get_success_url(self):
        return reverse('staff-promotion', kwargs={'code' : self.object.code})

class PercentagePromotionCreateView(PromotionCreateView):
    fields = ['code', 'max_uses', 'amount', 'min_spend', 'customer_limit', 'expiry', 'active', 'max_discount']
    template_name = 'promotions/new_percentage.html'
    
    def form_valid(self, form):
        form.instance.type = Promotion.PERCENTAGE
        return super().form_valid(form)
    
class FixedPromotionCreateView(PromotionCreateView):
    template_name = 'promotions/new_fixed.html'
    
    def form_valid(self, form):
        form.instance.type = Promotion.FIXED_PRICE
        return super().form_valid(form)

class PromotionUpdateView(StaffTestMixin, generic.UpdateView):
    model = Promotion
    fields = '__all__'
    slug_field = 'code'
    slug_url_kwarg = 'code'
    template_name = 'promotions/update.html'

    def get_success_url(self):
        return reverse('staff-promotion', kwargs={'code' : self.object.code})

class PromotionDeleteView(StaffTestMixin, generic.DeleteView):
    model = Promotion
    template_name = 'promotions/delete.html'
    slug_field = 'code'
    slug_url_kwarg = 'code'

    def get_success_url(self):
        return reverse('staff-promotions')

@user_passes_test(staff_check, login_url='staff-login')
def disable_promotions(request):
    Promotion.disable_all()
    return redirect('staff-promotions')

class DeliveryListView(generic.ListView):
    model = Delivery
    context_object_name = 'deliveries'
    template_name = 'delivery/index.html'

class DeliveryDetailView(generic.DetailView):
    model = Delivery
    template_name = 'delivery/detail.html'

class DeliveryCreateView(generic.edit.CreateView):
    model = Delivery
    fields = '__all__'
    template_name = 'delivery/new.html'

    def get_success_url(self):
        return reverse('staff-delivery', kwargs={'pk' : self.object.id})

class DeliveryUpdateView(generic.UpdateView):
    model = Delivery
    fields = '__all__'
    template_name = 'delivery/update.html'

    def get_success_url(self):
        return reverse('staff-delivery', kwargs={'pk' : self.object.id})

class DeliveryDeleteView(generic.DeleteView):
    model = Delivery
    template_name = 'delivery/delete.html'

    def get_success_url(self):
        return reverse('staff-deliveries')

class CarouselImageListView(generic.ListView):
    model = CarouselImage
    context_object_name = 'images'
    template_name = 'staff/home/carousel/index.html'

class CarouselImageDetailView(generic.DetailView):
    model = CarouselImage
    template_name = 'staff/home/carousel/detail.html'

class CarouselImageCreateView(generic.edit.CreateView):
    model = CarouselImage
    fields = '__all__'
    template_name = 'staff/home/carousel/new.html'

    def get_success_url(self):
        return reverse('staff-carousel', kwargs={'pk' : self.object.id})

class CarouselImageUpdateView(generic.UpdateView):
    model = CarouselImage
    fields = '__all__'
    template_name = 'staff/home/carousel/update.html'

    def get_success_url(self):
        return reverse('staff-carousel', kwargs={'pk' : self.object.id})

class CarouselImageDeleteView(generic.DeleteView):
    model = CarouselImage
    template_name = 'staff/home/carousel/delete.html'

    def get_success_url(self):
        return reverse('staff-carousel-index')