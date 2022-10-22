from django.shortcuts import redirect, render

from .forms import UploadFileForm

from .services import *


# Create your views here.

def plus(x):
    if x >= 0:
        return "+"  
    return "-"
    

def show_uploads_page(request):
   
    # process POST request
    if request.method == 'POST':
        if handle_uploaded_file(request.FILES.get('input_file', None), request.FILES.get('input_file', None).name):           
            update_input_file_name(request)
            if check_data_file(request):               
               
                f = UploadFileForm(request.POST)  
                f.is_valid()
                print(f.cleaned_data['file_format'])             
                if f.cleaned_data['file_format'] == 'table':
                    print('TABLE')
                    read_ok, inlines, xlines, x, y = read_table(get_full_filename(request.session['input_file_name']))
                    if not read_ok:
                        print('NOT OK')
                        f = UploadFileForm()
                        # initialize session variables
                        initialize_input_file_name(request)
                        return render(request, 'upload.html', {'form': f})
                    
                else:
                    read_ok, inlines, xlines, x, y = read_segy(get_full_filename(request.session['input_file_name']))
                    if not read_ok:
                        print('NOT OK')
                        f = UploadFileForm()
                        # initialize session variables
                        initialize_input_file_name(request)
                        return render(request, 'upload.html', {'form': f})

                regr_params = get_regression(inlines, xlines, x, y)
                x_formula = f"INLINE*{(regr_params.get('x_coefs')[0]):.2f} {plus(regr_params.get('x_coefs')[1])} XLINE*{abs(regr_params.get('x_coefs')[1]):.2f} {plus(regr_params.get('x_coefs')[2][0])} {abs(regr_params.get('x_coefs')[2][0]):.2f}"
                y_formula = f"INLINE*{(regr_params.get('y_coefs')[0]):.2f} {plus(regr_params.get('y_coefs')[1])} XLINE*{abs(regr_params.get('y_coefs')[1]):.2f} {plus(regr_params.get('x_coefs')[2][0])} {abs(regr_params.get('y_coefs')[2][0]):.2f}"
                inline_formula = f"X*{(regr_params.get('inline_coefs')[0]):.2f} {plus(regr_params.get('inline_coefs')[1])}Y*{abs(regr_params.get('inline_coefs')[1]):.2f} {plus(regr_params.get('inline_coefs')[2][0])} {abs(regr_params.get('inline_coefs')[2][0]):.2f}"
                xline_formula = f"X*{(regr_params.get('xline_coefs')[0]):.2f} {plus(regr_params.get('xline_coefs')[1])} Y*{abs(regr_params.get('xline_coefs')[1]):.2f}  {plus(regr_params.get('xline_coefs')[2][0])} {abs(regr_params.get('xline_coefs')[2][0]):.2f}"

                return render(request, 'upload.html', {'inline_min_max': f"{min(inlines)}-{max(inlines)}", 
                                                       'xline_min_max': f"{min(xlines)}-{max(xlines)}",
                                                       'x_min_max': f"{min(x)}-{max(x)}",
                                                       'y_min_max': f"{min(y)}-{max(y)}",
                                                       'x_formula': x_formula,
                                                       'y_formula': y_formula,
                                                       'inline_formula': inline_formula,
                                                       'xline_formula': xline_formula,
                                                       'X0': f"{regr_params.get('X0'):.2f}",
                                                       'Y0': f"{regr_params.get('Y0'):.2f}",
                                                       'alpha': f"{regr_params.get('alpha'):.2f}",
                                                       'step': f"{regr_params.get('step'):.2f}",
                                                       'inline_along_y': regr_params.get('inline_along_y'),
                                                       'form': f})


        # process GET request
    
    f = UploadFileForm()
        # initialize session variables
    initialize_input_file_name(request)
    return render(request, 'upload.html', {'form': f})


def show_about_page(request):
  
    return render(request, 'about.html')

