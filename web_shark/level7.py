#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
    ***************************************************************************

                                Shark evolution version: 1.0.4

    ***************************************************************************
    Алгоритм: Shark evolution
    Разработчик: Ситала Николай
    mailbox: titan2169@yandex.ru
    Date: 12.06.2017
"""

import os
import sys
import math
import time
import copy
import random
import collections
import datetime
import logging
import threading

import numpy as np
from numpy import array

# import matplotlib.pyplot as plt
# from matplotlib.ticker import LinearLocator, FormatStrFormatter, MultipleLocator
# from matplotlib import cm, style
# from mpl_toolkits.mplot3d import axes3d

import config
import imexdata
import perfomance


# style.use('fivethirtyeight')
# plt.rcParams['font.size'] = 8
# plt.rcParams['font.family'] = 'Verdana'
# plt.rcParams['figure.figsize'] = [12, 9]
# plt.rcParams['text.latex.unicode'] = True

class Plancalc():
    """
    Расчет плановой емкости фигур в полосе
    :return:
    """
    unit_capacity = 0.0  # Емкость блока
    fact_capcity = 0.0  # Фактический объем фигур
    plan_residue = 0.0  # Планируемый отход
    plan_rows = 0.0  # Планируется строк
    plan_min_column = 0.0  # Необходимо мимнимум столбцов
    relax = []  # Релаксированный список фигур

    def partial(fg, ct):
        """ Разбор до простых списков init_figure and count_figure

        :return:
        """
        Plancalc.relax = []
        for b in zip(fg, ct):
            Plancalc.relax.extend([b[0] for t in range(b[1])])

    def report(long_strips, lim_figure):
        Plancalc.fact_capcity = sum(Plancalc.relax)
        Plancalc.plan_rows = math.ceil(Plancalc.fact_capcity / long_strips)
        Plancalc.unit_capacity = Plancalc.plan_rows * long_strips
        Plancalc.plan_residue = Plancalc.unit_capacity - Plancalc.fact_capcity
        Plancalc.plan_min_column = math.ceil(len(Plancalc.relax) / Plancalc.plan_rows)

        logging.info('*' * 30)
        logging.info('Plan figure')
        logging.info('Емкость блока {0}'.format(Plancalc.unit_capacity))
        logging.info('Фактический объем {0}'.format(Plancalc.fact_capcity))
        logging.info('Планируемый отход {0}'.format(Plancalc.plan_residue))
        logging.info('Планируется строк {0}'.format(Plancalc.plan_rows))
        logging.info('Необходимо столбцов {0}'.format(Plancalc.plan_min_column))
        logging.info('*' * 30)


class config_param():
    # Статический класс для передачи переменных в функции и классы
    lifecycle = None
    cloth = None
    box = None
    dist = None
    sep = None


def _calc_permutation(matrix_result):
    """
    Расчет кол-ва перестановок
    :return:
    """

    # _test_tuning()

    perm = {'00': 0, '01': 1, '10': 1, '11': 1, '02': 1, '12': 1, '20': 0, '21': 1, '22': 1}

    matrix = []  # Матрица состояний перестановок для каждой ячейки
    matrix_state = []

    for b in matrix_result:
        y = len(b)
        if y < config_param.cloth.lim_figure:
            r = [0 for h in range(0, config_param.cloth.lim_figure - y)]
            b.extend(r)
        matrix.append(b)

    for y in range(len(matrix)):
        tmp = []
        for x in range(len(matrix[y])):
            f = matrix[y][x]
            if f > 0:
                if y > 0:
                    triangle_B1 = matrix[y - 1][x]
                else:
                    triangle_B1 = 'N'
                if x > 0:
                    triangle_A2 = matrix[y][x - 1]
                else:
                    triangle_A2 = 'N'

                # Треугольник состояний
                if f == triangle_B1:
                    status_B1 = 0
                elif triangle_B1 == 'N':
                    status_B1 = 2
                else:
                    status_B1 = 1

                if f == triangle_A2:
                    status_A2 = 0
                elif triangle_A2 == 'N':
                    status_A2 = 2
                else:
                    status_A2 = 1

                if x > 0:
                    status_A2 = tmp[x - 1]

                keystat = str(status_A2) + str(status_B1)
                valrng = perm[keystat]
            else:
                valrng = 0
            tmp.append(valrng)
        matrix_state.append(tmp)

    return matrix_state


def runbeg(study_matrix, tuning_state, orm):

    index_column = 0

    try:
        while index_column < config_param.cloth.lim_figure:
            curow = 0
            cx = index_column + 1

            while curow < len(study_matrix) and cx < config_param.cloth.lim_figure:

                # Срез значений по анализируемому стобцу
                analiz = [study_matrix[b][index_column] for b in range(len(study_matrix))]

                # Текущее анализируемое значение на возможность перестановок
                fx = study_matrix[curow][cx]

                if fx is 0:
                    cx = index_column + 1
                    curow += 1

                elif fx in analiz:
                    # Блок поиска значения в анализируемом столбце и организация перестановок
                    btun = tuning_state[curow][index_column]
                    nx = study_matrix[curow][index_column]

                    if not fx == nx and btun > 1:
                        # Рокировка значений
                        study_matrix[curow][index_column] = fx
                        study_matrix[curow][cx] = nx

                        if index_column == 0:

                            trix = copy.deepcopy(study_matrix)
                            cpm = trix[curow]  # Извлекаем вложенный необходимый список
                            trix.pop(curow)  # Удаляем из общего массива влож. список

                            # Формируем новый срез с учетом удаления
                            newanz = [trix[b][index_column] for b in range(len(trix))]
                            index_fx = [b for b in range(len(newanz)) if fx == newanz[b]]

                            try:
                                max_fx = max(index_fx)
                            except Exception as ex:
                                pass

                            # Вставляем изяътый ранее срез
                            trix.insert(max_fx + 1, cpm)

                            # Расчет кол-ва перестановок ножей, если меньше то сохраняем новую матрицу
                            tmp = _calc_permutation(trix)

                            t = 0
                            for x in tmp:
                                t += sum(x)
                            if orm >= t:
                                if orm > t:
                                    orm = t
                                study_matrix = copy.deepcopy(trix)

                                return 1, study_matrix, orm

                            else:
                                study_matrix[curow][index_column] = nx
                                study_matrix[curow][cx] = fx

                if cx < config_param.cloth.lim_figure:
                    cx += 1
                else:
                    cx = index_column + 1
                    curow += 1

            index_column += 1

    except Exception as ex:
        pass

    return 0, study_matrix, orm


def _block_tuning(matrix_result):
    """
    Тюнинг блочных фигур, до-упаковка одинаковых фигур и снижение кол-ва перестановок ножей 
    :param matrix_result: 
    :return: 
    """
    tun = {'00': 0, '10': 1, '01': 1, '11': 2, '20': 1, '21': 2, '02': 1, '12': 2, '22': 2}

    matrix = []  # Матрица состояний перестановок для каждой ячейки
    tuning_state = []

    for b in matrix_result:
        y = len(b)
        if y < config_param.cloth.lim_figure:
            r = [0 for h in range(0, config_param.cloth.lim_figure - y)]
            b.extend(r)
        matrix.append(b)

    for y in range(len(matrix)):
        tmp = []
        for x in range(len(matrix[y])):
            f = matrix[y][x]
            if f > 0:
                if y > 0:
                    triangle_B1 = matrix[y - 1][x]
                else:
                    triangle_B1 = 'N'
                if y == len(matrix) - 1:
                    triangle_B3 = 'N'
                else:
                    triangle_B3 = matrix[y + 1][x]

                # Треугольник состояний
                if f == triangle_B1:
                    status_B1 = 0
                elif triangle_B1 == 'N':
                    status_B1 = 2
                else:
                    status_B1 = 1

                if f == triangle_B3:
                    status_B3 = 0
                elif triangle_B3 == 'N':
                    status_B3 = 2
                else:
                    status_B3 = 1

                # if x > 0:
                #     status_B3 = tmp[x - 1]

                keystat = str(status_B1) + str(status_B3)
                valrng = tun[keystat]
            else:
                valrng = 0
            tmp.append(valrng)
        tuning_state.append(tmp)

    return matrix, tuning_state


def _test_tuning(matrix_result):
    # matrix_result = [
    #     [130, 120],
    #     [250, 250, 250, 250, 250],
    #     [250, 250, 250, 250, 250],
    #     [250, 250, 250, 250, 250],
    #     [250, 250, 250, 250, 250],
    #     [250, 250, 250, 250, 250],
    #     [340, 300, 200, 160, 140, 110],
    #     [380, 310, 310, 250],
    #     [450, 430, 220, 150],
    #     [500, 400, 350],
    #     [580, 570, 100]
    # ]

    orignal_matrix = _calc_permutation(matrix_result)  # Расчет перестановок ножей
    orm = 0
    for x in orignal_matrix:
        orm += sum(x)

    m = 1
    while m:
        try:
            # Циклическая доукомплектация блоков
            study_matrix = copy.deepcopy(matrix_result)
            matrix, tuning_state = _block_tuning(study_matrix)  # Расчет весовой функции
            m, study_matrix, orm = runbeg(study_matrix, tuning_state, orm)
            matrix_result = copy.deepcopy(study_matrix)

        except Exception as ex:
            pass

    return _calc_permutation(matrix_result)


def _line_analyzer(matrix_result):
    """
    Анализатор блочных структур и отбор блочных структур
    Определение плохих блочных структур для переделки

    :return:
    """
    lenblock = []
    i = 0
    parent = matrix_result[0]
    for b in matrix_result:
        marker = []
        r = map(lambda x, y: [x, y], parent, b)
        for j in r:
            if j[0] is None and isinstance(j[1], int):
                marker.append(0)
            elif j[1] is None and isinstance(j[0], int):
                marker.append(0)
            elif j[0] == j[1]:
                marker.append(0)
            else:
                marker.append(1)
        if sum(marker):
            lenblock.append(i)
            i = 1
        else:
            i += 1
        parent = b
    lenblock.append(i)

    return max(lenblock)


def _full_line(matrix_result, segment):
    """ Определение плохих блочных структур для переделки

    :return:
    """
    temp = []
    structure = []
    noblock = []

    i = 0
    parent = matrix_result[0]

    for b in matrix_result:

        marker = []
        r = map(lambda x, y: [x, y], parent, b)
        for j in r:
            if j[0] is None and isinstance(j[1], int):
                marker.append(0)
            elif j[1] is None and isinstance(j[0], int):
                marker.append(0)
            elif j[0] == j[1]:
                marker.append(0)
            else:
                marker.append(1)

        if sum(marker):
            if i > segment:
                structure.extend(temp)
            else:
                noblock.extend(temp)
            temp = []
            i = 1
        else:
            i += 1

        temp.append(b)
        parent = b

    if i > segment:
        structure.extend(temp)
    else:
        noblock.extend(temp)

    return structure, noblock


def shark(init_figure, init_count, cycle=15, shark_life=300):
    # print('all figure', sum(init_count), sep=':')

    lattice_crystal = []  # Результат оптимизации (кристалическая решетка)

    for b in range(cycle):
        my = Ants_Main(init_figure, init_count,
                       life_ants=shark_life,
                       elit_ants=5,
                       start_pheromon=0.0001,
                       evaparation=0.15,
                       alfaweight=1.0,
                       visible_route=7.0,
                       size_fncr=config_param.cloth.long_strips, lim_figure=config_param.cloth.lim_figure)

        my.calc_distance()
        my.main()
        my._result_print()

        lattice_crystal.extend(my.bad_in)
        init_figure, init_count = my._bad_partial()

        # print('shark bad separation', b, len(init_figure), sep=': ')

        if sum(init_figure) == 0:
            break

    if sum(init_figure) > my.size_fncr - config_param.cloth.right_residue:
        # Если полос более чем 1 осталось тогда применять дооптимизацию
        # с шириной 1250мм-90мм

        logging.info('additional optimization figure {0}'.format(sum(init_count)))

        for b in range(cycle):
            my = Ants_Main(init_figure, init_count,
                           life_ants=shark_life,
                           elit_ants=5,
                           start_pheromon=0.0001,
                           evaparation=0.15,
                           alfaweight=1.0,
                           visible_route=1.0,
                           size_fncr=config_param.cloth.long_strips - config_param.cloth.right_residue,
                           lim_figure=config_param.cloth.lim_figure)

            my.calc_distance()
            my.main()
            my._result_print()
            lattice_crystal.extend(my.bad_in)
            init_figure, init_count = my._bad_partial()

            if sum(init_figure) == 0:
                break

    lattice_crystal.extend(my.bad_out)

    return lattice_crystal


def _wheel_ratio(allgroup, golden_ratio_figure):
    """
    Выбор фигур по принципу колеса рулетки с настраиваемы коэфициентом
    значимости
    :param allgroup:
    :param golden_ratio_figure:
    :return:
    """

    # Коэфициент отбора по максимальному количеству одинаковых фигур
    alfa_effect = config_param.box.alfa_effect
    reverse_figure = {b: 0 for b in allgroup}
    for b in allgroup:
        d = reverse_figure[b]
        reverse_figure[b] = d + 1

    agr = []
    lost_figure = []

    while reverse_figure:
        sumWeight = 0
        for b, v in list(reverse_figure.items()):
            sumWeight += v ** alfa_effect

        # Получение случайного числа в интервале (сумма знаментеля)
        rndValue = random.random()

        revlist = []
        runningTotal = []
        for b, v in list(reverse_figure.items()):
            runningTotal.append(v ** alfa_effect / sumWeight)
            revlist.append(b)

        left = 0.0
        right = 0.0
        for idx, val in zip(revlist, runningTotal):
            right += val
            if left < rndValue <= right:
                nx = idx
                for h in range(0, reverse_figure[nx]):
                    if len(agr) < golden_ratio_figure:
                        agr.append(nx)
                    else:
                        lost_figure.append(nx)
                del reverse_figure[nx]
                break

    return agr, lost_figure


def _golden_ratio_structure(init_figure, init_count):
    """
    Определение заполнения блоками
    :return:
    """
    group = list(zip(init_figure, init_count))
    descending_count = sorted(group, key=lambda x: x[1], reverse=True)

    allgroup = []
    for b in descending_count:
        for r in range(0, b[1], 1):
            allgroup.append(b[0])

    golden_ratio_figure = int(round(len(allgroup) * config_param.box.section, 0))
    agr, balance = _wheel_ratio(allgroup, golden_ratio_figure)

    newlist = set(agr)
    df = {b: 0 for b in newlist}

    for b in agr:
        df[b] += 1

    init_figure = []
    init_count = []

    for b, v in list(df.items()):
        init_figure.append(b)
        init_count.append(v)

    return init_figure, init_count, balance


class Ants_Distance(object):
    """ Create matrix distance

    """

    version = '1.0'

    def __init__(self, init_figure, init_count, size_fncr=1250, lim_figure=8):

        self.size_fncr = size_fncr  # Ширина полуограниченной полосы
        self.lim_figure = lim_figure  # Кол-во допустимых фигур в полосе

        self.agregator = []  # Пул блоков из 2 списков (номера фигуры + использ.
        # шкала для расчета расстояний

        self.matrix = []  # Матрица расстояний между фигурами
        self.figure_descending = []  # Список фигур отсортир по убыванию

        # Глобальная модель расчета фиксированній магнит или функция
        self.model = config_param.dist.distance_model

        self.view_formula = config_param.dist.model_fx  # Номер функции от 0
        self.modvalue = 2  # Поправочный добавочный коэфициент,
        # смещающий все значения расстояний, отрицательные значения становятся +

        self.begin_axis_x = -0.1  # Ось X
        self.begin_axis_y = -0.1  # Ось Y

        self.init_figure = init_figure
        self.init_count = init_count
        self.figure = {}

        self.plato = config_param.box.plato  # Флаг блочности одинаковых фигур в матрице расстояний

    def _relax_figure(self):
        """ Преобразование списка фигур в словарь
        ключ: номер, значение: размер фигуры

        Кол-во фигур делаем равным 1

        :return:
        """
        i = 0
        for y, b in enumerate(self.init_count):
            for r in range(0, b, 1):
                self.figure[i] = self.init_figure[y]
                i += 1

        return 0

    def _scale_distance(self, grad):
        """ Создание шкалы в диапазоне всегда от (- до +)
            при попадании значения 0 выбрасываем его из списка
            это удобно для построение графиков и исключения
            ошибок с делением на нуль.

        :param grad:
        :return:
        """
        # шаг одного деления
        try:
            app_index = grad / (len(self.figure))
        except ZeroDivisionError:
            logging.info("Ошибка деление на нуль {0}  {1}".format(grad, len(self.figure)))
            main_thread.flag_optimization = 'error'
            sys.exit()

        # Начальная отрицательная точка шкалы
        z = 0
        app_init = -grad / 2.01
        app2 = app_init + z

        # Шкала в ввиде списка
        grad_list = []
        for b in range(0, len(self.figure)):
            grad_list.append(app2)
            app2 = round(app2 + app_index, 3)

        if 0 in grad_list:
            grad += 0.111
            grad_list = self._scale_distance(grad)
        return grad_list

    def _formula_ax(self, number, x, y):
        """ Применяемые функции для расстояний

        """
        if 0 == number:
            # Колпак
            try:
                res = math.sin(x * x + y * y) / (x * x + y * y)
            except ZeroDivisionError:
                res = 0
        elif 1 == number:
            # Волна
            try:
                res = math.sin(x + y) / (x + y)
            except ZeroDivisionError:
                res = 0
        elif 2 == number:
            res = (x ** 2 + y ** 2)
        elif 3 == number:
            res = math.sin(x) * math.cos(y)
        else:
            res = 0
        return res

    def _matrix_distance(self, model=0):
        """ Создание таблицы расстояний

        """
        # Созд матрицы расстояний
        self.matrix = [[0] * len(self.figure) for b in self.figure]
        self.figure_descending = sorted(self.figure, reverse=True)

        # Выбор модели создания расстояний между фигурами
        if model == 0:
            for senior in enumerate(self.figure_descending):
                for younger_figure in self.figure_descending[senior[0]:]:
                    # Расчет расстояний на основе весов, расчетному весу ближе
                    # мелкие веса и дальше, больше веса чем собственный вес.
                    # Принцип зафиксированного магнита, все что меньше
                    # прилипает лучше и быстрее.

                    senior_figure = senior[1]

                    if self.figure[senior_figure] == self.figure[
                        younger_figure] and self.plato is 1:
                        # Коэфициент блочности одинаковых фигур "Плато"
                        ds = round(self.figure[senior_figure] / 100, 2) * 100
                    else:
                        ds = self.figure[senior_figure] / self.figure[
                            younger_figure] * 100

                    data = self.matrix[senior_figure]
                    data[younger_figure] = ds
                    self.matrix[senior_figure] = data

                    if self.figure[senior_figure] == self.figure[
                        younger_figure] and self.plato is 1:
                        # Коэфициент блочности одинаковых фигур "Плато"
                        ds = round(self.figure[senior_figure] / 100, 2) * 10
                    else:
                        ds = self.figure[younger_figure] / self.figure[
                            senior_figure] * 100

                    data = self.matrix[younger_figure]
                    data[senior_figure] = ds
                    self.matrix[younger_figure] = data
        else:
            # Эмуляция расстояний по графикам функций
            for b in enumerate(self.agregator):
                for s in self.agregator[b[0]:]:
                    ds = self._formula_ax(self.view_formula, s[1] +
                                          self.begin_axis_x, b[1][1] +
                                          self.begin_axis_y)
                    # Масштабирование
                    ds += self.modvalue

                    data = self.matrix[s[0]]
                    data[b[1][0]] = ds
                    self.matrix[s[0]] = data

                    data = self.matrix[b[1][0]]
                    data[s[0]] = ds
                    self.matrix[b[1][0]] = data

    def calc_distance(self):
        """ Создание точек отсчета для шкалы
            Создание расстояний на основе формул

        """
        self._relax_figure()

        # Число делений на графике
        grad_list = self._scale_distance(2.5)

        # Создаем пул доступных блоков из 2 списков
        self.agregator = list(zip(self.figure, grad_list))

        # расчет расстояний по выбранной модели
        self._matrix_distance(self.model)


class Ants_Main(Ants_Distance):
    """ Calculate Floor Cell No Rotatation

    """

    version = '1.0'

    def __init__(self, init_figure, init_count,
                 life_ants=1,
                 lim_time_hours=100,
                 elit_ants=50,
                 start_pheromon=0.0001,
                 evaparation=0.15,
                 alfaweight=0.05,
                 visible_route=2.5,
                 size_fncr=1250, lim_figure=8):

        # Вызов конструктора наследуемого класса
        Ants_Distance.__init__(self, init_figure, init_count,
                               size_fncr, lim_figure)

        self.lim_time_hours = lim_time_hours  # Лимит часов работы алгоритма
        self.start_pheromon = start_pheromon  # Начальное значение феромона
        self.elit_ants = elit_ants / life_ants  # Количество элитных муравьев
        self.evaparation = evaparation  # Коэф испарения феромона
        self.alfaweight = alfaweight  # Коэф веса следа феромона от 0
        self.visible_route = visible_route  # Коэф видимости при выборе маршрута
        self.life_ants = life_ants  # Время жизни муравьиной колонии

        self.jump = None  # Номер вершины для перехода
        self.nodes = None  # Словарь комбинаций всех вершин маршрутов в таблице без учета кол-ва
        self.local_route = {}  # локальные маршруты
        self.pheromon = []  # список показателей феромона

        self.figure_tabu = {}  # Физич наличие доступных размеров фигур и их кол-ва (Табу-Лист)
        self.olr = float('inf')  # Длинна оптимального маршрута

        self.optimal_path = None
        self.bad_out = []  # Полосы с фигурами неполной оптимизации
        self.bad_in = []  # Полосы с фигурами и остатком нуль

    def _diagram_distance(self):
        """ Создание диаграммы матрицы расстояний

        :return:
        """
        fig = plt.figure()
        fig.suptitle('Матрица расстояний', fontsize=16)
        ax = fig.add_subplot(111, projection='3d')

        p = [v for b, v in self.agregator]
        x = array(p)
        y = x.copy()
        x, y = np.meshgrid(x, y)
        z = array(self.matrix)

        surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap=cm.coolwarm,
                               linewidth=0, antialiased=True)

        r1 = []
        for r in self.matrix:
            r1.extend(r)

        ax.set_zlim(min(r1), max(r1))
        ax.zaxis.set_major_locator(LinearLocator(10))
        ax.zaxis.set_major_formatter(FormatStrFormatter('%.0002f'))

        # Расчет делений для подписей по осям
        pos = p.copy()
        ax.set_xticks(pos)
        ax.set_yticks(pos)

        # Подписи на осях
        column_names = self.figure_descending.copy()
        row_names = self.figure_descending.copy()
        ax.set_xticklabels(column_names, rotation='vertical')
        ax.set_yticklabels(row_names, rotation='vertical')
        ax.set_xlabel('Ось Y', labelpad=15)
        ax.set_ylabel('Ось X', labelpad=15)
        ax.set_zlabel('Расстояние')

        fig.colorbar(surf, shrink=0.5, aspect=5)
        plt.show()

    def _polar_charts(self, sizes):

        # The slices will be ordered and plotted counter-clockwise.
        labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
        # sizes = [25, 30, 45, 100]
        colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
        # explode = (0, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

        plt.pie(sizes, autopct='%1.0f%%', shadow=True, startangle=90)
        # Set aspect ratio to be equal so that pie is drawn as a circle.
        plt.axis('equal')
        plt.show()

    def _hist3d(self, phr):
        """
        Диаграмма состояния феромона 3d
        Demo of a histogram for 2 dimensional data as a bar graph in 3D.
        """
        fig = plt.figure()
        fig.suptitle('Взвешенное состояние феромона', fontsize=16)
        ax = fig.add_subplot(111, projection='3d')

        data_array = array(phr)
        data = []
        for b in phr:
            data.extend(b)
        data2 = array(data)

        hist, xedges, yedges = np.histogram2d(np.arange(data_array.shape[1]),
                                              np.arange(data_array.shape[0]),
                                              bins=len(data_array) - 1,
                                              range=[[0, len(data_array) * 2],
                                                     [0, len(data_array) * 2]])

        # hist - адрес ячейки в таблице куда должен отображатся результат
        # создает двумерные матрицы сеток по одномерным массивам
        x_data, y_data = np.meshgrid(xedges, yedges)

        # создает двумерные матрицы сеток по одномерным массивам
        # x_data, y_data = np.meshgrid(np.arange(data_array.shape[1]),
        #                              np.arange(data_array.shape[0]))
        x_data = x_data.flatten()
        y_data = y_data.flatten()
        z_data = data2.flatten()

        # Ширина и толщина одного блока
        m = 1.3
        dx = m * np.ones_like(z_data)
        dy = dx.copy()
        ax.bar3d(x_data, y_data, np.zeros(len(z_data)), dx, dy, z_data,
                 zsort='average', alpha=1)

        # Расчет делений для подписей по осям
        pos = [b + m / 2 for b in xedges]
        ax.set_xticks(pos)
        ax.set_yticks(pos)

        # Подписи на осях
        column_names = self.figure_descending.copy()
        row_names = self.figure_descending.copy()
        ax.set_xticklabels(column_names, rotation='vertical')
        ax.set_yticklabels(row_names, rotation='vertical')
        ax.set_xlabel('Ось Y', labelpad=15)
        ax.set_ylabel('Ось X', labelpad=15)
        ax.set_zlabel('Вес феромона')
        plt.show()

    def _difer_lim_ants(self, antlist, filing_band, band, filing_count):
        """ Диспетчер ограничений
         1. Глобальный запрет на переход в вершину если оставшееся
         кол-во вершин равно 0

         2. Локальный запрет на переход в вершину ширина которой больше
         оставшейся ширины полосы

        :param antlist:
        :param filing_band:
        :param band:
        :return:
        """
        # Список строго запрещенных вершин для перехода
        limtabu = [b[0] for b in list(self.figure_tabu.items()) if b[1] == 0]

        # Локальный запрет с учетом оставшейся ширины полосы
        differ = self.size_fncr - filing_band

        # Создаем разность списков, оставляем только то что не запрещено!
        gx = list(set(antlist) - set(limtabu))
        new_gx = []
        for k in gx:
            if self.figure[k] <= differ and filing_count > 0:
                new_gx.append(k)
        if new_gx:
            gx = new_gx
        else:
            band += 1
            filing_band = 0
            filing_count = self.lim_figure

        return gx, filing_band, band, filing_count

    def _construction(self):
        """ Ядро алгоритма, построение маршрута и длины цепи для всей колонии

        :return:
        """
        d = collections.deque(self.figure_descending)
        self.jump = random.randint(0, self.figure_descending[0])
        # Перестройка коллекции для начала обхода
        d.rotate(self.jump + 1)
        self.nodes = list(d)

        self.figure_tabu = {h: 1 for h in self.figure}
        # Вершину выбранную как точку начала - блокируем для перехода
        self.figure_tabu[self.jump] = 0

        newPoint = self.local_route[0]
        newPoint[0] = [self.jump, 0]
        self.local_route[0] = newPoint

        filing_band = self.figure[self.jump]
        filing_count = self.lim_figure
        filing_count -= 1
        i = 1  # индекс вершины в локальном маршруте
        band = 0  # Принадлежность полосе от 0
        mrht = self.local_route[0]

        # Jump переходы по маршрутам пока не выбранны все фигуры
        while sum(list(self.figure_tabu.values())) > 0:

            antlist = self.nodes.copy()
            args = self._difer_lim_ants(antlist, filing_band, band,
                                        filing_count)
            antlist, filing_band, band, filing_count = args

            sumWeight = 0.0  # Знаменатель
            for idx in antlist:
                try:
                    q = ((1 / self.matrix[self.jump][idx]) ** self.visible_route) \
                        * ((self.pheromon[self.jump][idx]) ** self.alfaweight)
                    sumWeight += q
                except ZeroDivisionError:
                    logging.info('Деление на ноль _construction')
                    main_thread.flag_optimization = 'error'
                    sys.exit()

            # Получение случайного числа в интервале (сумма знаментеля)
            rndValue = random.random()

            runningTotal = []
            for idx in antlist:
                q = ((1 / self.matrix[self.jump][idx]) ** self.visible_route) \
                    * ((self.pheromon[self.jump][idx]) ** self.alfaweight)

                runningTotal.append(q / sumWeight)

            left = 0.0
            right = 0.0
            # explode = [0]
            for idx, val in zip(antlist, runningTotal):
                right += val
                if left < rndValue <= right:
                    nx = idx
                    break

            # explode.append(right)
            #     left = right
            #
            # print(max(explode))
            #
            # size = tuple(explode)
            # self._polar_charts(size)
            idx = nx

            # Сохраняем номер фигуры для перехода
            self.jump = idx
            filing_count -= 1
            filing_band += self.figure[self.jump]
            pos = mrht[i]
            pos = [self.jump, band]
            mrht[i] = pos
            self.local_route[0] = mrht
            i += 1

            # Уменьшение кол-ва доступных фигур
            self.figure_tabu[self.jump] = 0

        return 0

    def _pheromone_add(self, local):
        """ Добавление феромона на ребро маршрута

        :return:
        """
        for b in range(0, len(local) - 1):
            bg = local[b]
            en = local[b + 1]

            idy = bg[0]
            pmn_y = self.pheromon[idy]

            idx = en[0]
            x = pmn_y[idx]
            pmn_y[idx] = x + self.elit_ants
            self.pheromon[idy] = pmn_y

        return 0

    def _best_solution(self, iter_time):
        """ Определение лучшего решения на текущей итерации

        :return:
        """
        temp_best = []
        for b in list(self.local_route.items()):
            name_route = b[0]
            local_route = b[1]

            # Начальная полоса
            band = local_route[0][1]
            fill = 0  # Остаток от заливки полосы
            all_fill = 0  # Общий остаток от заливки по 1 маршруту

            for r in local_route:
                if band == r[1]:
                    fill += self.figure[r[0]]
                else:
                    # Длинна маршрута без учета последней полосы
                    all_fill += self.size_fncr - fill
                    fill = 0
                    fill += self.figure[r[0]]
                    band = r[1]
            temp_best.append([name_route, all_fill])
        local_best = sorted(temp_best, key=lambda x: x[1])

        self._evaporation()
        if self.optimal_path:
            local = self.local_route[local_best[0][0]]
            self._pheromone_add(local)

        if local_best[0][1] < self.olr:
            self.olr = local_best[0][1]
            self.optimal_path = self.local_route[local_best[0][0]]
        else:
            pass

        return 0

    def _evaporation(self):
        """ Испарение феромона со всех граней,
            увеличение испарения от кол-ва фигур

        :return:
        """
        for ph in self.pheromon:
            for b in range(0, len(ph)):
                m = ph[b]
                if m > self.start_pheromon:
                    ph[b] = m * (1 - self.evaparation)
                else:
                    ph[b] = self.start_pheromon
        return 0

    def _result_print(self):
        """ Вывод результата

        :return:
        """
        band_out = []
        band = []
        parent = [0, 0]

        # Сортировка значений внутри 1 полосы
        for t in self.optimal_path:
            if not t[1] == parent[1]:
                band1 = sorted(band, reverse=True)
                band_out.append(band1)
                band = []
            band.append(self.figure[t[0]])
            parent = t

        bs = sorted(band, reverse=True)
        band_out.append(bs)

        fisum = 0
        for b in enumerate(band_out):
            fisum += len(b[1])
            d = self.size_fncr - sum(b[1])
            if 0 == d:
                # Всплываем как взбитая фракция и храним пул
                self.bad_in.append(b[1])
            else:
                # Тяжелый осадок оседает в оотдельный пул
                self.bad_out.append(b[1])

    def _bad_partial(self):
        """ Возврат части плохого результата для повторной обработки
        в формате простых списков init_figure and count_figure

        :return:
        """
        fg = []
        ct = []
        for b in self.bad_out:
            ct.extend([1 for t in b])
            fg.extend(b)
        return fg, ct

    def main(self):
        """ Main Logic Unit

        :return:
        """
        self.pheromon = [[self.start_pheromon] * len(self.figure)
                         for b in enumerate(self.figure)]

        # self._diagram_distance()

        # Время жизни муравьиной колонии
        for iter_time in range(0, self.life_ants):
            # Инициализация массива локальных маршрутов
            # на текущей итерации колонии
            # [0, 0] - означает,  индекс 0 хранит выбранную фигуру,
            # индекс 1 хранит принадлежность полосе шириной устан шириной
            self.local_route = {b: [[0, 0]] * len(self.figure)
                                for b in range(1)}

            # Постр. маршрута и длины цепи для всей колонии
            self._construction()
            self._best_solution(iter_time)

            # *******************************************
            # Досрочный выход в случае отказа от подписки
            if main_thread.stopping:
                main_thread.flag_optimization = None
                main_thread.stopping = False
                sys.exit()

                # *******************************************

        # self._hist3d(self.pheromon)

        return 0


def _shark_gold(init_figure, init_count):
    # print('all figure', sum(init_count), sep=':')

    lattice_crystal = []  # Результат оптимизации

    for b in range(config_param.sep.gold_cycle):
        my = Ants_Main(init_figure, init_count,
                       life_ants=config_param.sep.gold_life,
                       elit_ants=5,
                       start_pheromon=0.0001,
                       evaparation=0.15,
                       alfaweight=2.2,
                       visible_route=0.5,
                       size_fncr=config_param.cloth.long_strips, lim_figure=config_param.cloth.lim_figure)

        my.calc_distance()
        my.main()
        my._result_print()

        lattice_crystal.extend(my.bad_in)
        init_figure, init_count = my._bad_partial()

        if sum(init_figure) == 0:
            break

    lattice_crystal.extend(my.bad_out)

    return lattice_crystal


def _sector_gold(init_figure, init_count, lentask, *args):
    block_pyramid = []  # Блочный список или пирамида
    fill = config_param.cloth.long_strips
    loop = config_param.box.loop

    detail_percent = lentask / loop  # Расчет прогресса в выделенной доле

    for b in range(loop):

        if main_thread.progress + detail_percent < 100.0:
            main_thread.progress += detail_percent

        # main_thread.progress += detail_percent
        # print(main_thread.progress)

        flim = round(sum(init_count) * config_param.box.lim_list, 0)  # Допустимый остаток списка
        # balance Большая часть нерасчитанного остатка
        fraction_black = []  # Черный список, включает неоптим. полосы и balance

        if b < loop - 1 and sum(init_count) > flim:
            init_figure, init_count, balance = _golden_ratio_structure(
                init_figure, init_count)

            result = _shark_gold(init_figure, init_count)

            for z in result:
                if fill - sum(z) == 0:
                    block_pyramid.append(z)
                else:
                    fraction_black.extend(z)
            fraction_black.extend(balance)

            init_count = [1 for j in fraction_black]
            init_figure = fraction_black
        else:
            if args[0][0] is 1 and args[0][1] <= 1:
                shark_life = config_param.lifecycle.shark_last
                cycle = config_param.lifecycle.cycle_last
            else:
                shark_life = config_param.lifecycle.shark_regular
                cycle = config_param.lifecycle.cycle_regular

            result = shark(init_figure, init_count, cycle, shark_life)
            for z in result:
                block_pyramid.append(z)
            break

    # print('result')
    # block_pyramid = sorted(block_pyramid, reverse=False)
    # for x in block_pyramid:
    #     print(x)

    return block_pyramid


def _level_optimization(event):
    """
    Расчет показателей уровня оптимизации

    :return:
    """

    line = 0
    logging.info("-")
    logging.info('*' * 30)
    logging.info('Emerald door')
    logging.info('*' * 30)
    matrix_result = sorted(event, reverse=False)

    for x in matrix_result:
        if not sum(x) == config_param.cloth.long_strips:
            line += 1
        logging.info(x)

    logging.info('кол-во полос {0}'.format(len(matrix_result)))
    logging.info('незаполнено полос на 100% {0}'.format(line))
    logging.info('-')

    logging.info('permutation start')
    # matrix_state = _calc_permutation(matrix_result)
    matrix_state = _test_tuning(matrix_result)
    mp = 0
    for x in matrix_state:
        mp += sum(x)
        logging.info(x)

    logging.info('permutation end')

    res = {'matrix_result': matrix_result, 'matrix_state': matrix_state, 'full_line': len(matrix_result),
           'bad_line': line,
           'permutation': mp}

    return res


def consolidation_figures(fi, cn, knox, limright, site_attempt):
    """ Главный сборщик упорядоченных болчных структур с минимальным остатком

    :param fi:
    :param cn:
    :return:
    """

    def call_back(bad_consol):
        """
        Разложение плохих блочных структур в линейные списки

        :param bad_consol:
        :return:
        """
        init_figure = []
        init_count = []

        if bad_consol:
            for h in bad_consol:
                init_figure.extend(h)
            init_count = [1 for j in init_figure]
        return init_figure, init_count

    Essence = {}  # Хранение сущностей после выхода из колеса реинкарнаций
    gltm = 0  # Общий счетчик полученных раскладок

    # Обновляем кол-во сущностей по запросу пользователя
    perfomance.update_attempt(site_attempt)

    percent = (95 / perfomance.attempt)

    # Генератор кармических задач для сущностей
    gen = perfomance._development()
    for b in range(perfomance.attempt):

        # config_param.cloth, config_param.box, config_param.dist, config_param.lifecycle, config_param.sep, task_fate = next(gen)
        config_param.box, config_param.dist, config_param.lifecycle, config_param.sep, task_fate = next(gen)
        config_param.cloth = perfomance._cloth(long_strips=1250, right_residue=limright, lim_figure=knox)

        Plancalc.partial(fi, cn)
        Plancalc.report(config_param.cloth.long_strips, config_param.cloth.lim_figure)

        logging.info('-' * 30)
        logging.info('Fate {0}'.format(b + 1))
        logging.info('-' * 30)
        logging.info('{0}'.format(config_param.cloth))
        logging.info('{0}'.format(config_param.box))
        logging.info('{0}'.format(config_param.dist))
        logging.info('{0}'.format(config_param.lifecycle))
        logging.info('{0}'.format(config_param.sep))
        logging.info('{0}'.format(task_fate))

        init_figure = fi
        init_count = cn
        bad_consol = []
        seven = []  # Белая часть сущности при выходе из цикла реинкарнаций
        reincarnation = len(task_fate)  # Кол-во попыток улучшения кармы сущности (задачи)

        while reincarnation:

            logging.info('-')
            logging.info('---Wheel of reincarnation--- {0}'.format(reincarnation))
            logging.info('-')

            all_structure = []  # Структура текущей реинкарнации
            layout = task_fate[reincarnation]  # Задача для текущей реинкарнации
            segment = len(layout) - 1
            lentask = percent / len(task_fate) / len(layout)
            # print('lentask', lentask)

            logging.info('layout {0}'.format(layout))

            if sum(init_count) == 0:
                logging.info('bad start layout, sum init_count = {0}'.format(0))
                limprogress = main_thread.progress + (percent / len(task_fate))
                if limprogress < 100.0:
                    main_thread.progress += percent / len(task_fate)
                # print('bad', percent / len(task_fate))
                break

            # Количество итераций нахождения блочных сегментов
            while segment + 1:
                i = 0
                correct_consol = []

                logging.info('Отобрано фигур {0}  {1}'.format(b, sum(init_count)))

                if sum(init_count) == 0:
                    break
                block_pyramid = _sector_gold(init_figure, init_count, lentask, [reincarnation, segment + 1])
                bad_consol = []

                s = 0
                while s < len(block_pyramid) - 1:
                    if block_pyramid[s] == block_pyramid[s + 1]:
                        i = 1
                        correct_consol.append(block_pyramid[s])
                    else:
                        if s > 0 and block_pyramid[s] == block_pyramid[s - 1]:
                            correct_consol.append(block_pyramid[s])
                        else:
                            i = 0
                            bad_consol.append(block_pyramid[s])
                    s += 1
                if i == 1:
                    correct_consol.append(block_pyramid[s])
                else:
                    bad_consol.append(block_pyramid[s])

                correct_consol.extend(bad_consol)
                matrix_result = sorted(correct_consol, reverse=False)

                logging.info('segment {0}  {1}'.format(segment, layout[segment]))
                structure, bad_consol = _full_line(matrix_result, layout[segment])
                init_figure, init_count = call_back(bad_consol)

                all_structure.extend(structure)
                segment -= 1

                logging.info('call_back {0}'.format(segment + 1))

            all_structure.extend(bad_consol)

            # Минимальный уровень для выхода из колеса реинкарнаций min_level_reincarnation
            min_level = _line_analyzer(all_structure)  # Анализатор блочных структур
            # Опред плохих блочных структур для переделки
            structure, bad_consol = _full_line(all_structure, min_level - 1)

            init_figure, init_count = call_back(bad_consol)
            seven.extend(structure)
            reincarnation -= 1

            # if sum(init_count) is 0:
            #     break

        seven.extend(bad_consol)
        res = _level_optimization(copy.deepcopy(seven))
        Essence[gltm] = res
        gltm += 1

    main_thread.progress = 100

    return Essence


def start(pull_figure, knox, limright, site_attempt):
    logging.info('Started')
    logging.info('Start optimization: {0}'.format(str(datetime.datetime.now())))

    init_figure = [b[0] for b in pull_figure]
    init_count = [b[1] for b in pull_figure]

    Essence = consolidation_figures(init_figure, init_count, knox, limright, site_attempt)

    logging.info('End >>>> {0}'.format(str(datetime.datetime.now())))

    logging.info('*' * 30)
    logging.info('Achieved_optimization')

    # Определение лучшей сущности
    temp = []
    for b in Essence:
        r = Essence[b]
        temp.append([b, r['full_line'], r['bad_line'], r['permutation']])
        logging.info('iter{0} full_line {1}  bad_line {2}, permutation{3}'.format(b, r['full_line'], r['bad_line'],
                                                                                  r['permutation']))

    bestresult = sorted(temp, key=lambda x: (x[2], x[3]))
    ex = bestresult[0]

    logging.info('*' * 30)
    logging.info(str(ex[0]))

    return [Essence[ex[0]], config_param.cloth.long_strips]


def standart():
    """ Стандартная реализация Shark evolution без надстроек блочных структур
        используется стандартное сепарирование по остатку = 0

    :return:
    """
    global init_figure, init_count

    exm_path = os.path.join(config.exm, 'myapp.log')
    logging.basicConfig(filename=exm_path, level=logging.INFO, filemode='w')
    logging.info('Started')

    filename = os.path.join(config.exm, 'result', 'standart_shark.xlsx')
    normpathfile = os.path.normpath(filename)

    # Генератор кармических задач для сущностей
    gen = perfomance._development()
    config_param.cloth, config_param.box, config_param.dist, config_param.lifecycle, config_param.sep, task_fate = next(
        gen)
    Plancalc.partial(init_figure, init_count)
    Plancalc.report(config_param.cloth.long_strips, config_param.cloth.lim_figure)

    lattice_crystal = shark(init_figure, init_count)
    lattice_crystal_sort = sorted(lattice_crystal)
    res = _level_optimization(copy.deepcopy(lattice_crystal_sort))

    imexdata.saveExcel([res, config_param.cloth.long_strips], normpathfile)


class main_thread(threading.Thread):
    """Worker Thread Class."""

    resdict = []  # Результат в виде списка
    stopping = None  # Подписка внешнего клиента
    flag_optimization = None
    progress = 0  # Процент выполнения

    def __init__(self, pull_figure, knox=8, limright=90, site_attempt=1):
        """Init Worker Thread Class."""

        threading.Thread.__init__(self)
        self.pull_figure = pull_figure
        self.knox = knox
        self.limright = limright
        self.site_attempt = site_attempt


    def run(self):
        main_thread.flag_optimization = 'start'

        try:
            main_thread.resdict = start(self.pull_figure, self.knox, self.limright, self.site_attempt)
            main_thread.flag_optimization = 'stop'
        except Exception as ex:
            main_thread.flag_optimization = 'error'
            logging.info(ex)
            logging.info(self.pull_figure)
            # print(ex)
            # print(self.pull_figure)


class main_thread_two():
    """Worker Thread Class."""

    resdict = []  # Результат в виде списка
    stopping = None  # Подписка внешнего клиента
    flag_optimization = None
    progress = 0  # Процент выполнения

    def __init__(self, pull_figure, knox=8, limright=90, site_attempt=1):
        """Init Worker Thread Class."""

        self.pull_figure = pull_figure
        self.knox = knox
        self.limright = limright
        self.site_attempt = site_attempt

    def run(self):

        main_thread.flag_optimization = 'start'
        try:
            main_thread.resdict = start(self.pull_figure, self.knox, self.limright, self.site_attempt)
            main_thread.flag_optimization = 'stop'
        except Exception as ex:
            logging.info(ex)
            main_thread.flag_optimization = 'error'


if __name__ == '__main__':
    # init_figure = [250, 150, 200, 160, 170, 330, 130, 300, 350, 180, 230,
    #                270, 280, 310, 380, 110, 210, 220, 240, 340, 360, 370,
    #                390, 400, 450, 500, 600, 660, 320]
    #
    # init_count = [60, 50, 40, 30, 30, 25, 25, 20, 20, 15, 10, 10, 10, 10, 10,
    #               10, 5, 5, 5, 5, 5, 5, 5, 3, 3, 2, 1, 1, 5]

    init_figure = [100, 160, 270, 350, 200, 250, 330, 320]

    init_count = [5, 3, 3, 3, 5, 5, 5, 2]

    # init_figure = [650, 600, 420, 390, 380, 370, 360, 340, 330, 320, 290,
    #                280, 270, 260, 250, 250, 240, 230, 220, 210, 200, 200,
    #                190, 180, 170, 160, 150, 150, 140, 120, 100]
    #
    # init_count = [1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 8, 2, 2, 2, 3, 3,
    #               10, 3, 3, 2, 3, 2, 6, 1, 1, 1, 2]

    init_figure = [150, 190, 250, 210, 170, 180, 90, 200, 270, 290, 100, 110, 220, 130, 230, 350, 160, 300, 310, 370,
                   390, 410, 430, 450, 490]

    init_count = [14, 14, 10, 8, 6, 2, 5, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1]

    standart()
