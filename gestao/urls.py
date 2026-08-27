from django.urls import path
from .views import (
    SolicitacaoListView,
    SolicitacaoCreateView,
    SolicitacaoUpdateView,
    AtendimentoCreateView,
    RelatorioGerencialView,
    exportar_relatorio_pdf
)

urlpatterns = [
    path('', SolicitacaoListView.as_view(), name='solicitacao_list'),
    path('solicitacao/nova/', SolicitacaoCreateView.as_view(), name='solicitacao_create'),
    path('solicitacao/<int:pk>/editar/', SolicitacaoUpdateView.as_view(), name='solicitacao_update'),
    path('solicitacao/<int:pk>/atender/', AtendimentoCreateView.as_view(), name='atendimento_create'),
    path('relatorio/', RelatorioGerencialView.as_view(), name='relatorio'),
    path('relatorio/pdf/', exportar_relatorio_pdf, name='relatorio_pdf'),
]
