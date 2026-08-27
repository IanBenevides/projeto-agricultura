from django.db import models

class Solicitacao(models.Model):
    EQUIPAMENTO_CHOICES = [
        ('TRATOR', 'Trator'),
        ('RETROESCAVADEIRA', 'Retroescavadeira'),
    ]

    SERVICO_TRATOR_CHOICES = [
        ('ARAR', 'Arar'),
        ('GRADEAR', 'Gradear'),
        ('SULCAR', 'Sulcar'),
        ('ENCANTEIRAR', 'Encanteirar'),
    ]

    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]

    nome_produtor = models.CharField(max_length=255, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, verbose_name="CPF")
    endereco = models.CharField(max_length=255, verbose_name="Endereço")
    localidade = models.CharField(max_length=100, verbose_name="Localidade")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    
    data_solicitacao = models.DateField(auto_now_add=True, verbose_name="Data da Solicitação")
    equipamento = models.CharField(max_length=20, choices=EQUIPAMENTO_CHOICES, verbose_name="Equipamento")
    tipo_servico = models.CharField(max_length=20, choices=SERVICO_TRATOR_CHOICES, blank=True, null=True, verbose_name="Tipo de Serviço")
    descricao = models.TextField(verbose_name="Descrição do Serviço")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")

    def __str__(self):
        return f"{self.nome_produtor} - {self.equipamento} - {self.status}"

class Atendimento(models.Model):
    solicitacao = models.OneToOneField(Solicitacao, on_delete=models.CASCADE, related_name='atendimento', verbose_name="Solicitação")
    data_atendimento = models.DateField(verbose_name="Data do Atendimento")
    nome_operador = models.CharField(max_length=255, verbose_name="Nome do Tratorista/Operador")
    horas_trabalhadas = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Horas Trabalhadas")
    horimetro = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Marcação do Horímetro")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.solicitacao.status = 'CONCLUIDO'
            self.solicitacao.save()

    def __str__(self):
        return f"Atendimento: {self.solicitacao.nome_produtor} - {self.data_atendimento}"
