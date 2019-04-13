from .models import Message
from django import forms


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)

    def clean(self):
        cleaned_data = super(MessageForm, self).clean()
        sender = cleaned_data.get('sender')
        receiver = cleaned_data.get('receiver')
        content = cleaned_data.get('content')
        if not sender and not receiver and not content:
            raise forms.ValidationError('You have to write something!')




