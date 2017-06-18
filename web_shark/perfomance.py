#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import collections

ROOT_PATH = os.path.dirname(__file__)

# the enclosed structure

# attempt
#   |
#   |__reincarnation (all task_fate)
#       |
#       |__layout (task_fate)
#           |
#           |__loop
#               |
#               |__gold_cycle
#               |     |__gold_life
#               |
#               |__cycle_regular
#               |     |__shark_regular
#               |     |__shark_last
#               |
#               |__cycle_last
#                     |__shark_regular
#                     |__shark_last


# ********** Доп. коэфициенты скорость - качество *****************************************

# Время жизни колонии shark в процессе жизни сущности и на последней итерации
_lifecycle = collections.namedtuple('shark_life', ['cycle_regular',
                                                   'cycle_last',
                                                   'shark_regular',
                                                   'shark_last'])

# ********** Ограничение полотна и кол-ва фигур *******************************************
# long_strips = 1250  # Длинна полосы в милиметрах
# right_residue = 90  # Минимальный допустимый остаток справа
# lim_figure = 8      # Допустимое количество фигур в 1 полосе

_cloth = collections.namedtuple('control_cloth', ['long_strips',
                                                  'right_residue',
                                                  'lim_figure'])

# ********** Коэфициенты блочных структур *************************************************
# section = 0.26        # Доля сечение списка от 100% для разворота фигур в блоки
# lim_list = 0.10       # Допустимый необрабатываемый остаток
# alfa_effect = 7.2     # Коэф. видимости фигур, чем выше тем больше видит фигуры с макс. кол-вом
# plato = 1             # Коэфициент Доп. блочности 0 - не использовать, 1 - включить
# loop = 20             # Количество попыток создания блочности _sector_gold

_box = collections.namedtuple('box_structure', ['section',
                                                'lim_list',
                                                'alfa_effect',
                                                'plato',
                                                'loop'])

# ********** Коэфициенты матрицы расстояний ***********************************************
# distance_model = 0    # Глобальная модель расчета фиксированный магнит или график функции
# model_fx = 1          # Номер графика функции, если выбрано distance_model = 1

_dist = collections.namedtuple('coeff_distances', ['distance_model',
                                                   'model_fx'])

# ********** Коэфициенты циклов сепарирования остатка в 0 *********************************
# gold_cycle = 10   # Кол-во попыток сепарирования полос без остатка в _shark_gold
# gold_life = 10    # Время жизни колонии в _shark_gold

_sep = collections.namedtuple('separation', ['gold_cycle',
                                             'gold_life'])

# val = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# g = _perf._make(val)


# Количество выращиваемых сущностей
attempt = 1


def _development():
    """ Индивидуальный план развития сущностей

    :return:
    """
    global attempt

    q = collections.deque()

    # cloth = _cloth(long_strips=1250, right_residue=90, lim_figure=8)
    lifecycle = _lifecycle(cycle_regular=10, cycle_last=15, shark_regular=60, shark_last=300)
    separation = _sep(gold_cycle=15, gold_life=100)
    dist = _dist(distance_model=0, model_fx=0)

    # Программа развития сущщности "A"
    task_fate_A = {}

    layout_task = []
    layout_task.extend([5] * 1)
    task_fate_A[2] = layout_task

    layout_task = []
    layout_task.extend([1] * 10)
    layout_task.extend([2] * 5)
    layout_task.extend([3] * 3)
    layout_task.extend([4] * 2)
    task_fate_A[1] = layout_task

    # Программа развития сущщности "B"
    task_fate_B = {}

    layout_task = []
    layout_task.extend([3] * 1)
    task_fate_B[2] = layout_task

    layout_task = []
    layout_task.extend([1] * 5)
    layout_task.extend([2] * 3)
    task_fate_B[1] = layout_task


    box = _box(section=0.26, lim_list=0.10, alfa_effect=7.2, plato=1, loop=25)
    # q.append([cloth, box, dist, lifecycle, separation, task_fate])
    q.append([box, dist, lifecycle, separation, task_fate_A])

    box = _box(section=0.25, lim_list=0.15, alfa_effect=7.1, plato=1, loop=25)
    q.append([box, dist, lifecycle, separation, task_fate_B])

    box = _box(section=0.24, lim_list=0.20, alfa_effect=7.0, plato=1, loop=25)
    q.append([box, dist, lifecycle, separation, task_fate_A])

    box = _box(section=0.23, lim_list=0.25, alfa_effect=6.9, plato=1, loop=25)
    q.append([box, dist, lifecycle, separation, task_fate_B])

    box = _box(section=0.22, lim_list=0.30, alfa_effect=6.8, plato=1, loop=25)
    q.append([box, dist, lifecycle, separation, task_fate_A])


    # Организация циклического конвеера задач
    for b in range(attempt):
        develop = q[0]
        q.rotate(-1)

        yield (develop)

    return 0


def update_attempt(site_attempt):
    # Обновление кол-ва сущностей по запросу пользовтаеля

    global attempt
    attempt = site_attempt