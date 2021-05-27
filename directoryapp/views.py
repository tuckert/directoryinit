from django.shortcuts import render
from directoryapp import models
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView, ModelFormMixin, ProcessFormView
from django.views.generic.detail import DetailView, SingleObjectTemplateResponseMixin
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import send_sms, random_string_generator, get_client_ip
from django.urls import reverse
from django.forms import formset_factory, inlineformset_factory
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from . import forms
from django.db import transaction
from django.shortcuts import HttpResponseRedirect
from django.core import serializers


class CreateUpdateView(SingleObjectTemplateResponseMixin, ModelFormMixin, ProcessFormView):

    def get_object(self, queryset=None):
        try:
            return super(CreateUpdateView,self).get_object(queryset)
        except AttributeError:
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(CreateUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(CreateUpdateView, self).post(request, *args, **kwargs)


class OnlyUsersDirectoriesMixin:
    def get_queryset(self):
        return self.request.user.directories.all()


# Create your views here.
class ListDirectoryView(OnlyUsersDirectoriesMixin, LoginRequiredMixin, ListView):
    model = models.Directory
    fields = '__all__'
    template_name = 'directory_list.html'


class CreateDirectoryView(LoginRequiredMixin, CreateView):
    model = models.Directory
    # fields = '__all__'
    template_name = 'directory_form.html'
    form_class = forms.CreateDirectoryForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(CreateDirectoryView, self).form_valid(form)


class UpdateDirectoryView(LoginRequiredMixin, UpdateView):
    model = models.Directory
    fields = '__all__'
    template_name = 'directory_form.html'


class DeleteDirectoryView(LoginRequiredMixin, DeleteView):
    model = models.Directory
    fields = '__all__'
    template_name = 'directory_form.html'


class DetailDirectoryView(OnlyUsersDirectoriesMixin, LoginRequiredMixin, DetailView):
    template_name = 'directory_detail.html'
    model = models.Directory


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'


class CreateInvitationView(LoginRequiredMixin, FormView):
    form_class = forms.CreateInvitationFromScratchForm
    template_name = 'create_invitation.html'
    invitation = None

    def form_valid(self, form):
        try:
            if self.kwargs['tenant']:
                tenant = models.Tenant.objects.get(pk=self.kwargs['tenant'])
            else:
                tenant = None
        except KeyError:
            tenant = None
        inv = models.Invitation.objects.create(
            directory=models.Directory.objects.get(slug=self.kwargs['slug']),
            max_uses=3,
            name_sent_to=form.cleaned_data['tenant_name'],
            number_sent_to=form.cleaned_data['tenant_number'],
            email_sent_to=form.cleaned_data['tenant_email'],
            tenant=tenant
        )
        self.invitation = inv
        current_site = get_current_site(self.request)
        uid = urlsafe_base64_encode(force_bytes(inv.id))
        token = account_activation_token.make_token(inv)
        link = "http://" + current_site.domain + reverse('use-invitation', kwargs={'uidb64': uid, 'token': token})
        inv.link = link
        inv.save()
        if form.cleaned_data['send_via'] in ['tx', 'bo']:
            message = 'Hello ' + form.cleaned_data['tenant_name'] + '! Message from app.  ' + link
            send_sms(form.cleaned_data['tenant_number'], message)
        if form.cleaned_data['send_via'] in ['em', 'bo']:
            send_mail(
                'Link inside to submit your information into the front gate directory',
                'Please click this link and submit your information as it should appear in the new gate directory: ' + link,
                'tuckert@gmail.com',
                [form.cleaned_data['tenant_email']],
                fail_silently=False,
            )
        return super(CreateInvitationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('invitation', kwargs={'pk': self.invitation.id})


class InvitationUsageView(CreateUpdateView):
    model = models.Tenant
    form_class = forms.CreateTenantFromInvitationForm
    template_name = 'invitation_usage.html'
    invitation = None
    numbers_formset = None
    tenant = None

    def get_success_url(self):
        return reverse('thank-you')

    def get_object(self, queryset=None):
        if self.invitation.tenant:
            obj = self.invitation.tenant
        else:
            print('Making new Tenant obj')
            obj = models.Tenant(
                name=self.invitation.name_sent_to,
                directory=self.invitation.directory,
            )
        return obj

    # Verify token and set self.invitation
    def dispatch(self, request, *args, **kwargs):

        try:
            uid = force_str(urlsafe_base64_decode(self.kwargs['uidb64']))
            self.invitation = models.Invitation.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError):
            self.invitation = None

        if self.invitation is not None and account_activation_token.check_token(self.invitation, self.kwargs['token']):
            return super(InvitationUsageView, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    # Add number formsets to context
    def get_context_data(self, **kwargs):
        context = super(InvitationUsageView, self).get_context_data(**kwargs)
        NumberFormset = inlineformset_factory(
            models.Tenant,
            models.TelephoneNumber,
            max_num=self.invitation.directory.max_telephones_per_tenant,
            extra=self.invitation.directory.max_telephones_per_tenant,
            fields='__all__'
        )
        if self.request.POST:
            self.numbers_formset = NumberFormset(
                self.request.POST,
                instance=self.object,
            )
        else:
            self.numbers_formset = NumberFormset(
                        instance=self.object
            )
        context['number_formset'] = self.numbers_formset
        return context

    # Create Tenant
    def form_valid(self, form):
        with transaction.atomic():
            form.directory = self.invitation.directory
            self.object = form.save(commit=False)
            self.object.directory = self.invitation.directory
            self.object.save()
            self.get_context_data()
            self.invitation.tenant = self.object
            self.invitation.save()
            if self.numbers_formset.is_valid():
                tenant_numbers = self.numbers_formset.save()
            else:
                return self.render_to_response(self.get_context_data())
        print(get_client_ip(self.request))
        print(form.has_changed())
        print(self.numbers_formset.has_changed())
        print(serializers.serialize("json", tenant_numbers+[self.object]))
        if form.has_changed() or self.numbers_formset.has_changed():
            print('making invitation usage')
            models.InvitationUsage.objects.create(
                invitation=self.invitation,
                ip_address=get_client_ip(self.request),
                fields_updated=serializers.serialize("json", tenant_numbers+[self.object])
            )
        return HttpResponseRedirect(self.get_success_url())


class InvitationDetailView(LoginRequiredMixin, DetailView):
    template_name = 'invitation_detail.html'
    model = models.Invitation


class ListInvitationView(LoginRequiredMixin, ListView):
    model = models.Invitation
    fields = '__all__'
    template_name = 'invitation_list.html'

    def get_queryset(self):
        return models.Invitation.objects.filter(directory__owner=self.request.user)


class ThankYouView(TemplateView):
    template_name = 'thank_you.html'


class TenantDetailView(OnlyUsersDirectoriesMixin, DetailView):
    template_name = 'tenant_detail.html'

    def get_queryset(self):
        queryset = super(TenantDetailView, self).get_queryset()
        queryset = queryset.filter(slug=self.kwargs['slug'])
        return models.Tenant.objects.filter(directory__in=queryset)


class TenantListView(OnlyUsersDirectoriesMixin, ListView):
    template_name = 'tenant_list.html'
    model = models.Tenant

    def get_queryset(self):
        queryset = super(TenantListView, self).get_queryset()
        directory = queryset.get(slug=self.kwargs['slug'])
        return directory.tenants.all()