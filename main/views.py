from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import * 
from django.contrib.auth.views import *
from .forms import LoginForm, UserEntryForm, ClinicInviteForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.urls import reverse, reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import generic 
from .enums import *
import re
# Create your views here.
class Login(LoginView): # 追加
    """ログインページ"""
    form_class = LoginForm
    template_name = 'login.html'

class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'login.html'


class UserEntryView(generic.FormView):
    form_class = UserEntryForm
    template_name = 'user_entry.html'
    success_template = 'user_entry_completed.html'
    invalid_operation_template = 'user_entry_invalid_operation.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic_instance'] = Clinic.objects.get(id = self.request.GET.get('clinic'))
        context['time_frame_dict'] = TIME_FRAME_DICT
        context['day_of_week_dict'] = DAY_OF_WEEK_DICT
        context['operation_dict'] = OPERATION_DICT
        context['email'] = self.request.GET.get('email')
        context['clinic'] = self.request.GET.get('clinic')
        
        email = self.request.GET.get('email')
        clinic = self.request.GET.get('clinic')
        try:
            instance = UserEntry.objects.get(email = email, clinic = clinic)
        except UserEntry.DoesNotExist:
            pass
        else:
            print(instance)
            context['instance'] = instance
        return context

    def form_valid(self, form):
        instance = form.save(commit = True)
        instance.additional_items.all().delete()
        
        params = self.request.POST.copy()
        additional_fields = [key for key in params if re.fullmatch(r'\d+\-\d+', key)]
        for additional_field in additional_fields:
            (field_id, option_id) = additional_field.split('-')
            field_instance = ClinicAdditionalField.objects.get(id = field_id)
            option_instance = ClinicAdditionalFieldOption.objects.get(id = option_id)

            additional_item = UserEntryAdditionalItem(parent = instance, question = field_instance, chosen_option = option_instance)
            additional_item.save()
        return render(self.request, self.success_template)

    def form_invalid(self, form):
        print(form.errors)
        print('form invalid')
        return super().form_invalid(form)   

    def get(self, request, **kwargs):
        if 'clinic' not in request.GET or 'email' not in request.GET:
            return render(request, self.invalid_operation_template)
        
        return super().get(request, **kwargs)

class UserEntryCompletedView(generic.TemplateView):
    template_name = 'user_entry_completed.html'

class ClinicAdminView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'clinic_admin.html'
    create_form_class = ClinicInviteForm
    create_form = create_form_class()

    def get(self, request, **kwargs):
        self.create_form = self.create_form_class()
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        action = request.POST.get('action') or None
        if action == 'start':
            params = request.POST.copy()
            params['clinic'] = request.user.id
            create_form = self.create_form_class(params or None)
            additional_fields = [key for key in params if re.fullmatch(r'\d+\-\d+', key)]

            if create_form.is_valid():
                # if success
                instance = create_form.save()
                for additional_field in additional_fields:
                    (field_id, option_id) = additional_field.split('-')
                    field_instance = ClinicAdditionalField.objects.get(id = field_id)
                    option_instance = ClinicAdditionalFieldOption.objects.get(id = option_id)

                    additional_item = ClinicInviteAdditionalItem(parent = instance, question = field_instance, chosen_option = option_instance)
                    additional_item.save()

                messages.success(request, '登録内容を保存しました。')
    
        elif action == 'end':
            for (key, on_or_off) in request.POST.items():
                if 'invite' in key and on_or_off == 'on':
                    (_, invite_id) = key.split('_')
                    instance_to_delete = get_object_or_404(ClinicInvite, id = int(invite_id))
                    
                    for user_entry in instance_to_delete.matched_user_entries:
                        user_entry.notify_invite_taken(instance_to_delete)
                    instance_to_delete.delete()
                    messages.success(request, 'ID:{}の募集を停止しました'.format(invite_id))
            
        #return render(request, self.template_name, context = self.get_context_data())
        return redirect('main:clinicadmin')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_form"] = self.create_form
        context["object_list"] = ClinicInvite.objects.filter(clinic = self.request.user)
        return context

class ListUserEntryView(LoginRequiredMixin, generic.ListView):
    template_name = 'list_user_entry.html'
    model = UserEntry
    
    def get_queryset(self):
        return UserEntry.objects.filter(clinic = self.request.user)
    