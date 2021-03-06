from staff.models import FAQ, Message, Promotion, Delivery, CarouselImage
from django.views import generic
from django.urls import reverse
from django.shortcuts import redirect
from .views import staff_check, StaffTestMixin
from django.contrib.auth.decorators import user_passes_test

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

class PromotionView(StaffTestMixin):
    model = Promotion
    slug_field = 'code'
    slug_url_kwarg = 'code'
    fields = ['code', 'max_uses', 'amount', 'min_spend', 'expiry', 'active']

    def get_success_url(self):
        return reverse('staff-promotion', kwargs={'code' : self.object.code})

class PromotionDetailView(PromotionView, generic.DetailView):
    template_name = 'promotions/detail.html'

class PercentagePromotionCreateView(PromotionView, generic.edit.CreateView):
    fields = ['code', 'max_uses', 'amount', 'min_spend', 'expiry', 'active', 'max_discount']
    template_name = 'promotions/percentage.html'

    def form_valid(self, form):
        form.instance.type = Promotion.PERCENTAGE
        return super().form_valid(form)
    
class FixedPromotionCreateView(PromotionView, generic.edit.CreateView):
    template_name = 'promotions/fixed.html'
    
    def form_valid(self, form):
        form.instance.type = Promotion.FIXED_PRICE
        return super().form_valid(form)

class PromotionUpdateView(PromotionView, generic.UpdateView):
    template_name = 'promotions/fixed.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.type == Promotion.PERCENTAGE:
            self.fields += ['max_discount']
            self.template_name = 'promotions/percentage.html'
        return super().get(request, *args, **kwargs)

class PromotionDeleteView(PromotionView, generic.DeleteView):
    def get(self, request, code):
        return redirect('staff-promotions')

    def get_success_url(self):
        return reverse('staff-promotions')

@user_passes_test(staff_check, login_url='staff-login')
def disable_promotions(request):
    Promotion.disable_all()
    return redirect('staff-promotions')

class DeliveryView(StaffTestMixin):
    model = Delivery
    fields = '__all__'
    template_name = 'delivery/view.html'

    def get_success_url(self):
        return reverse('staff-deliveries')

class DeliveryListView(StaffTestMixin, generic.ListView):
    model = Delivery
    context_object_name = 'deliveries'
    template_name = 'delivery/index.html'

class DeliveryCreateView(DeliveryView, generic.edit.CreateView): pass

class DeliveryUpdateView(DeliveryView, generic.UpdateView): pass

class DeliveryDeleteView(DeliveryView, generic.DeleteView):
    def get(self, request, pk):
        return redirect('staff-deliveries')

class CarouselImageListView(StaffTestMixin, generic.ListView):
    model = CarouselImage
    context_object_name = 'images'
    template_name = 'staff/home/carousel/index.html'

class CarouselImageDetailView(StaffTestMixin, generic.DetailView):
    model = CarouselImage
    template_name = 'staff/home/carousel/detail.html'

class CarouselImageCreateView(StaffTestMixin, generic.edit.CreateView):
    model = CarouselImage
    fields = '__all__'
    template_name = 'staff/home/carousel/new.html'

    def get_success_url(self):
        return reverse('staff-carousel', kwargs={'pk' : self.object.id})

class CarouselImageUpdateView(StaffTestMixin, generic.UpdateView):
    model = CarouselImage
    fields = '__all__'
    template_name = 'staff/home/carousel/update.html'

    def get_success_url(self):
        return reverse('staff-carousel', kwargs={'pk' : self.object.id})

class CarouselImageDeleteView(StaffTestMixin, generic.DeleteView):
    model = CarouselImage
    template_name = 'staff/home/carousel/delete.html'

    def get_success_url(self):
        return reverse('staff-carousel-index')

class MessageListView(StaffTestMixin, generic.ListView):
    model = Message
    context_object_name = 'messages'
    template_name = 'staff/messages/index.html'
    
class MessageDeleteView(StaffTestMixin, generic.DeleteView):
    model = Message

    def get(self, request, pk):
        return redirect('staff-messages')

    def get_success_url(self):
        return reverse('staff-messages')