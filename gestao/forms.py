import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Solicitacao, Atendimento

def validar_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido.')
    
    # Cálculo dos dígitos verificadores
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if str(digit) != cpf[i]:
            raise ValidationError('CPF inválido.')

class TailwindFormMixin:
    """
    Mixin to dynamically inject CSS classes into form widgets.
    This prepares the form for a Design System like Tailwind CSS.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            base_classes = "block w-full rounded-xl border-gray-300 shadow-sm focus:border-brand-blue focus:ring-brand-blue sm:text-sm py-2.5 px-3 bg-white border transition-colors"
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_classes} {base_classes}".strip()

class SolicitacaoForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ['nome_produtor', 'cpf', 'endereco', 'localidade', 'telefone', 'equipamento', 'tipo_servico', 'descricao']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name in ['equipamento', 'tipo_servico']:
            if field_name in self.fields:
                field = self.fields[field_name]
                # Traduzir o empty_label padrão do Django ('---------')
                new_choices = [('', 'Selecione uma opção')] + [c for c in field.choices if c[0] != '']
                field.choices = new_choices
                
                # Adicionar validação HTML5
                field.required = True
                field.widget.attrs.update({
                    'required': 'required',
                    'oninvalid': "this.setCustomValidity('Por favor, selecione uma opção.')",
                    'onchange': "this.setCustomValidity('')"
                })

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            validar_cpf(cpf)
        return cpf

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone and not re.match(r'^\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}$', telefone):
            raise forms.ValidationError("Formato de telefone inválido.")
        return telefone

    def clean(self):
        cleaned_data = super().clean()
        equipamento = cleaned_data.get('equipamento')
        tipo_servico = cleaned_data.get('tipo_servico')
        
        if not tipo_servico:
            self.add_error('tipo_servico', 'Selecione o tipo de serviço.')
        elif equipamento == 'TRATOR' and not tipo_servico.startswith('TRATOR_'):
            self.add_error('tipo_servico', 'Selecione um serviço válido para trator.')
        elif equipamento == 'RETROESCAVADEIRA' and not tipo_servico.startswith('RETRO_'):
            self.add_error('tipo_servico', 'Selecione um serviço válido para retroescavadeira.')
            
        return cleaned_data

class AtendimentoForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = ['data_atendimento', 'nome_operador', 'horas_trabalhadas', 'horimetro_inicial', 'horimetro_final', 'descricao']
        widgets = {
            'data_atendimento': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def clean_horas_trabalhadas(self):
        horas = self.cleaned_data.get('horas_trabalhadas')
        if horas is not None and horas <= 0:
            raise forms.ValidationError("As horas trabalhadas devem ser maiores que zero.")
        return horas

    def clean(self):
        cleaned_data = super().clean()
        horimetro_inicial = cleaned_data.get('horimetro_inicial')
        horimetro_final = cleaned_data.get('horimetro_final')

        if horimetro_inicial is not None and horimetro_inicial < 0:
            self.add_error('horimetro_inicial', "A marcação inicial não pode ser negativa.")
        
        if horimetro_final is not None and horimetro_final < 0:
            self.add_error('horimetro_final', "A marcação final não pode ser negativa.")
            
        if horimetro_inicial is not None and horimetro_final is not None:
            if horimetro_final < horimetro_inicial:
                self.add_error('horimetro_final', "A marcação final não pode ser menor que a inicial.")

        return cleaned_data
