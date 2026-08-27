from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.db.models import Sum, Count
from .models import Solicitacao, Atendimento
from .forms import SolicitacaoForm, AtendimentoForm

class SolicitacaoListView(ListView):
    model = Solicitacao
    template_name = 'gestao/solicitacao_list.html'
    context_object_name = 'solicitacoes'

    def get_queryset(self):
        queryset = super().get_queryset()
        localidade = self.request.GET.get('localidade')
        status = self.request.GET.get('status')
        if localidade:
            queryset = queryset.filter(localidade__icontains=localidade)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

class SolicitacaoCreateView(CreateView):
    model = Solicitacao
    form_class = SolicitacaoForm
    template_name = 'gestao/solicitacao_form.html'
    success_url = reverse_lazy('solicitacao_list')

class SolicitacaoUpdateView(UpdateView):
    model = Solicitacao
    form_class = SolicitacaoForm
    template_name = 'gestao/solicitacao_form.html'
    success_url = reverse_lazy('solicitacao_list')

class AtendimentoCreateView(CreateView):
    model = Atendimento
    form_class = AtendimentoForm
    template_name = 'gestao/atendimento_form.html'
    success_url = reverse_lazy('solicitacao_list')

    def form_valid(self, form):
        form.instance.solicitacao_id = self.kwargs.get('pk')
        return super().form_valid(form)

import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def get_relatorio_context(request):
    localidade = request.GET.get('localidade')
    if localidade == 'None':
        localidade = ''
        
    data_inicial = request.GET.get('data_inicial')
    if data_inicial == 'None':
        data_inicial = ''
        
    data_final = request.GET.get('data_final')
    if data_final == 'None':
        data_final = ''
    
    # Query base para as solicitações
    solicitacoes_base = Solicitacao.objects.all().select_related('atendimento').order_by('-data_solicitacao')
    
    if localidade:
        solicitacoes_base = solicitacoes_base.filter(localidade=localidade)
    
    if data_inicial:
        solicitacoes_base = solicitacoes_base.filter(data_solicitacao__gte=data_inicial)
        
    if data_final:
        solicitacoes_base = solicitacoes_base.filter(data_solicitacao__lte=data_final)
        
    data_inicial_obj = None
    data_final_obj = None
    if data_inicial:
        try:
            data_inicial_obj = datetime.datetime.strptime(data_inicial, '%Y-%m-%d').date()
        except ValueError:
            pass
    if data_final:
        try:
            data_final_obj = datetime.datetime.strptime(data_final, '%Y-%m-%d').date()
        except ValueError:
            pass
            
    context = {}
    context['solicitantes'] = solicitacoes_base
    context['localidades'] = Solicitacao.objects.values_list('localidade', flat=True).distinct().order_by('localidade')
    context['selected_localidade'] = localidade
    context['data_inicial'] = data_inicial
    context['data_final'] = data_final
    context['data_inicial_obj'] = data_inicial_obj
    context['data_final_obj'] = data_final_obj
    
    # Total de horas trabalhadas por equipamento (aplicando o filtro se houver)
    horas_trator = Atendimento.objects.filter(solicitacao__in=solicitacoes_base, solicitacao__equipamento='TRATOR').aggregate(total=Sum('horas_trabalhadas'))['total'] or 0
    horas_retro = Atendimento.objects.filter(solicitacao__in=solicitacoes_base, solicitacao__equipamento='RETROESCAVADEIRA').aggregate(total=Sum('horas_trabalhadas'))['total'] or 0
    
    # Volume de demandas por localidade
    demandas_localidade = solicitacoes_base.values('localidade').annotate(total=Count('id')).order_by('-total')
    
    context['horas_trator'] = horas_trator
    context['horas_retro'] = horas_retro
    context['demandas_localidade'] = demandas_localidade
    return context

class RelatorioGerencialView(TemplateView):
    template_name = 'gestao/relatorio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_relatorio_context(self.request))
        return context

import os
from django.conf import settings

def get_file_uri(filename):
    full_path = os.path.join(settings.BASE_DIR, 'static', 'image', filename)
    # Convert backslashes to forward slashes and prepend file:///
    forward_slash_path = str(full_path).replace('\\', '/')
    return f"file:///{forward_slash_path}"

def exportar_relatorio_pdf(request):
    template_path = 'gestao/relatorio_pdf.html'
    context = get_relatorio_context(request)
    context['data_emissao'] = datetime.datetime.now()
    context['logo_inovai'] = get_file_uri('inovailogo-removebg-preview.png')
    context['logo_smcti'] = get_file_uri('logosmcti-removebg-preview.png')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_patrulha_agricola.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(
        html, dest=response
    )
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

