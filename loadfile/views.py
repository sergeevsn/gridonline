from django.shortcuts import redirect, render, HttpResponse

from .forms import UploadFileForm

from .services import *


# Create your views here.

def plus(x):
    if x >= 0:
        return "+"  
    return "-"

def point_string(inline, xline, x, y):
    return f"INLINE:{inline}, XLINE:{xline}, X:{x}, Y:{y}"

def get_xy_from_inline_xline(inline, xline, coefs_x, coefs_y):
    print(type(inline), type(xline))
    print(coefs_x[0])
    print(coefs_x[1])
    print(coefs_y[0])
    print(coefs_y[1])
    x = inline*coefs_x[0] + xline*coefs_x[1] + coefs_x[2]
    y = inline*coefs_y[0] + xline*coefs_y[1] + coefs_y[2]
    return x, y
    

def show_uploads_page(request):
   
    # process POST request
    if request.method == 'POST':
        if handle_uploaded_file(request.FILES.get('input_file', None), request.FILES.get('input_file', None).name):           
            update_input_file_name(request)
            if check_data_file(request):               
               
                f = UploadFileForm(request.POST)  
                f.is_valid()
                          
                if f.cleaned_data['file_format'] == 'table':
                  
                    read_ok, inlines, xlines, x, y = read_table(get_full_filename(request.session['input_file_name']))
                    if not read_ok:
                       
                        f = UploadFileForm()
                        # initialize session variables
                        initialize_input_file_name(request)
                        return render(request, 'upload.html', {'form': f})
                    
                else:
                    read_ok, inlines, xlines, x, y = read_segy(get_full_filename(request.session['input_file_name']))
                    if not read_ok:
                       
                        f = UploadFileForm()
                        # initialize session variables
                        initialize_input_file_name(request)
                        return render(request, 'upload.html', {'form': f})
                inl_step = np.mean(np.diff(np.sort(np.unique(inlines))))
                xln_step = np.mean(np.diff(np.sort(np.unique(xlines))))
                regr_params = get_regression(inlines, xlines, x, y)
                request.session['regr_params'] = regr_params
                x_formula = f"INLINE*{(regr_params.get('x_coefs')[0]):.3f} {plus(regr_params.get('x_coefs')[1])} XLINE*{abs(regr_params.get('x_coefs')[1]):.3f} {plus(regr_params.get('x_coefs')[2])} {abs(regr_params.get('x_coefs')[2]):.3f}"
                y_formula = f"INLINE*{(regr_params.get('y_coefs')[0]):.3f} {plus(regr_params.get('y_coefs')[1])} XLINE*{abs(regr_params.get('y_coefs')[1]):.3f} {plus(regr_params.get('x_coefs')[2])} {abs(regr_params.get('y_coefs')[2]):.3f}"
                inline_formula = f"X*{(regr_params.get('inline_coefs')[0]):.3f} {plus(regr_params.get('inline_coefs')[1])}Y*{abs(regr_params.get('inline_coefs')[1]):.3f} {plus(regr_params.get('inline_coefs')[2])} {abs(regr_params.get('inline_coefs')[2]):.3f}"
                xline_formula = f"X*{(regr_params.get('xline_coefs')[0]):.3f} {plus(regr_params.get('xline_coefs')[1])} Y*{abs(regr_params.get('xline_coefs')[1]):.3f}  {plus(regr_params.get('xline_coefs')[2])} {abs(regr_params.get('xline_coefs')[2]):.3f}"

                first_point_inline = min(inlines)
                first_point_xline = min(xlines)
                first_point_x, first_point_y = get_xy_from_inline_xline(first_point_inline, first_point_xline, regr_params.get('x_coefs'), regr_params.get('y_coefs'))
                second_point_inline = min(inlines)
                second_point_xline = max(xlines)
                second_point_x, second_point_y = get_xy_from_inline_xline(second_point_inline, second_point_xline, regr_params.get('x_coefs'), regr_params.get('y_coefs'))
                third_point_inline = max(inlines)
                third_point_xline = max(xlines)
                third_point_x, third_point_y = get_xy_from_inline_xline(third_point_inline, third_point_xline, regr_params.get('x_coefs'), regr_params.get('y_coefs'))
                

                return render(request, 'upload.html', {'inline_min_max': f"{min(inlines)}-{max(inlines)}({int(inl_step)})", 
                                                       'xline_min_max': f"{min(xlines)}-{max(xlines)}({int(xln_step)})",
                                                       'x_min_max': f"{min(x)}-{max(x)}",
                                                       'y_min_max': f"{min(y)}-{max(y)}",
                                                       'x_formula': x_formula,
                                                       'y_formula': y_formula,
                                                       'inline_formula': inline_formula,
                                                       'xline_formula': xline_formula,
                                                       'X0': f"{regr_params.get('X0'):.2f}",
                                                       'Y0': f"{regr_params.get('Y0'):.2f}",
                                                       'alpha': f"{regr_params.get('alpha'):.3f}",
                                                       'step': f"{regr_params.get('step'):.2f}",
                                                       'inline_along_y': regr_params.get('inline_along_y'),
                                                       'first_point_inline': first_point_inline,
                                                       'first_point_xline': first_point_xline,
                                                       'first_point_x': f"{first_point_x:.2f}",
                                                       'first_point_y': f"{first_point_y:.2f}",
                                                       'second_point_inline': second_point_inline,
                                                       'second_point_xline': second_point_xline,
                                                       'second_point_x': f"{second_point_x:.2f}",
                                                       'second_point_y': f"{second_point_y:.2f}",
                                                       'third_point_inline': third_point_inline,
                                                       'third_point_xline': third_point_xline,
                                                       'third_point_x': f"{third_point_x:.2f}",
                                                       'third_point_y': f"{third_point_y:.2f}",

                                                       
                                                       'form': f})


        # process GET request
    
    f = UploadFileForm()
        # initialize session variables
    initialize_input_file_name(request)
    return render(request, 'upload.html', {'form': f})


def show_about_page(request):
  
    return render(request, 'about.html')

def calc_xy(request):
    if request.method == 'POST':
        if not request.session['regr_params']:
            return HttpResponse('')
        regr_params = request.session['regr_params']
        
     
        x, y = get_xy_from_inline_xline(int(request.POST.get('inline')[0]), int(request.POST.get('xline')[0]), regr_params.get('x_coefs'), regr_params.get('y_coefs'))
        
        return HttpResponse(f"X={x:.2f}, Y={y:.2f}")
        
    return HttpResponse('')


