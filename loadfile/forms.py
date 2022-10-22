from django import forms

class UploadFileForm(forms.Form):
    input_file = forms.FileField(label='Upload Table or SEG-Y file:', widget=forms.FileInput(attrs={'class': 'control'}))   
    CHOISES = [("table", "Space separated text file"), ("SEG-Y", "Seismic data in SEG-Y format")]
    file_format = forms.ChoiceField(choices=CHOISES)

