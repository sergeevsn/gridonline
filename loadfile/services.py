import os
import pandas as pd
from pandas.errors import ParserError
import numpy as np
import segyio as sgy
import math
import time

from django.conf import settings


def get_full_filename(fname):
    return os.path.join(settings.BASE_DIR, 'data', fname)


def handle_uploaded_file(f, fname):
    """ Загрузка файла на сервер """
    try:
        with open(get_full_filename(fname), 'wb+') as destination:

            for chunk in f.chunks():
                destination.write(chunk)

    except OSError:
        return False
    finally:
        return True


def initialize_input_file_name(request):
    """ инициализация имен файлов в сессии """
    request.session['input_file_name'] = ''


def update_input_file_name(request):
    """ обновление имен файлов после загрузки из формы """
    request.session['input_file_name'] = request.FILES.get('input_file', None).name


def check_data_file(request):
    """ Проверка файлов """
    if not (request.session['input_file_name']):
        print('Нет имени файла в сессии')
        return False
    return True


def read_segy(filename):
    read_ok = True
    x_coords = []
    y_coords = []
    try:
        with sgy.open(filename, ignore_geometry=True) as segyfile:
            segyfile.mmap()
            inlines = [segyfile.header[i][sgy.TraceField.INLINE_3D] for i in range(segyfile.tracecount)]
            xlines = [segyfile.header[i][sgy.TraceField.CROSSLINE_3D] for i in range(segyfile.tracecount)]
            x_coords = [segyfile.header[i][sgy.TraceField.CDP_X] for i in range(segyfile.tracecount)]
            y_coords = [segyfile.header[i][sgy.TraceField.CDP_Y] for i in range(segyfile.tracecount)]
            scaler = abs(segyfile.header[1][sgy.TraceField.SourceGroupScalar])
    except (UnboundLocalError, RuntimeError):
        read_ok = False
        return read_ok, None, None, None, None

    os.remove(filename)
    if not (scaler == 0):
        x = list(map(lambda n: n/scaler, x_coords))
        y = list(map(lambda n: n/scaler, y_coords))
    else:
        x = x_coords
        y = y_coords
    return read_ok, inlines, xlines, x, y


def read_table(filename):
    read_ok = True
    try:
        df = pd.read_csv(filename, delim_whitespace=True)
    except (UnicodeDecodeError, ParserError):
        read_ok = False
        return read_ok, None, None, None, None
    df.columns = [col.lower() for col in df.columns]
    for i, col in enumerate(df.columns):
        if col == 'crossline':
            df.columns[i] = 'xline'
        if col == 'iline':
            df.columns[i] = 'inline'
        if col == 'cdp_x':
            df.columns[i] = 'x'
        if col == 'cdp_y':
            df.columns[i] = 'y'

    if not 'inline' in df.columns:
        print('Не найден столбец inline/iline')
        return
    if not 'xline' in df.columns:
        print('Не найден столбец crossline/xline')
        return
    if not 'x' in df.columns:
        print('Не найден столбец x/cdp_x')
        return
    if not 'y' in df.columns:
        print('Не найден столбец y/cdp_y')
        return

    os.remove(filename)

    return read_ok, df.inline, df.xline, df.x, df.y


def get_regression(inlines, xlines, x, y):
    X = np.vstack([inlines, xlines]).T
    X = np.c_[X, np.ones(X.shape[0])]
    linregX = np.linalg.lstsq(X, np.array(x), rcond=None)[0]
    linregY = np.linalg.lstsq(X, np.array(y), rcond=None)[0]

    X = np.vstack([x, y]).T
    X = np.c_[X, np.ones(X.shape[0])]
    linregInl = np.linalg.lstsq(X, np.array(inlines), rcond=None)[0]
    linregXln = np.linalg.lstsq(X, np.array(xlines), rcond=None)[0]

    step = np.sqrt(linregX[0] ** 2 + linregX[1] ** 2)
    inline_along_y = math.copysign(1.0, linregX[0] * linregY[1]) == -1

    # вариант через тангенс даёт верный результат в 1 и 4 четвертях. Вариант через косинус - в 1 и 2
    # учитывая, что 1 и 4 наиболее частый вариант, то оставляю тангенс
    if inline_along_y:

        alpha = np.degrees(np.arctan(linregX[0] / linregX[1]))
    else:

        alpha = np.degrees(np.arctan(linregX[1] / linregX[0]))

    return {
        'x_coefs': linregX.tolist(),
        'y_coefs': linregY.tolist(),
        'inline_coefs': linregInl.tolist(),
        'xline_coefs': linregXln.tolist(),
        'X0': linregX[0] + linregX[1] + linregX[2],
        'Y0': linregY[0] + linregY[1] + linregY[2],
        'step': step,
        'inline_along_y': inline_along_y,
        'alpha': alpha,
    }

def get_xy_from_inline_xline(inline, xline, coefs_x, coefs_y):
    x = inline * coefs_x[0] + xline * coefs_x[1] + coefs_x[2]
    y = inline * coefs_y[0] + xline * coefs_y[1] + coefs_y[2]
    return x, y

def get_inline_xline_from_x_y(x, y, inline_coefs, xline_coefs):
    inline = x * inline_coefs[0] + y * inline_coefs[1] + inline_coefs[2]
    xline = x * xline_coefs[0] + y * xline_coefs[1] + xline_coefs[2]
    return inline, xline
