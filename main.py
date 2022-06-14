import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import  StandardScaler
import scipy.stats as stats
from scipy.signal import savgol_filter
from scipy.signal import find_peaks
from math import ceil
    
calendar = []
timer = []
acc_x = []
acc_y = []
acc_z = []
gyro_x = []
gyro_y = []
gyro_z = []
counter = []

# funkcja, która czyści konsolę
def clear_console():
    os.system('cls')


# funkcja odpowiadająca za komunikację z użytkownikiem podczas wczytania pliku
def start():
    clear_console()
    calendar.clear()
    timer.clear()
    acc_x.clear()
    acc_y.clear()
    acc_z.clear()
    gyro_x.clear()
    gyro_y.clear()
    gyro_z.clear()
    counter.clear()
    print("-----------------------------------------------------------------------------------------------------------")
    print("                                              START                                                        ")
    print("-----------------------------------------------------------------------------------------------------------")
    file_directory = "data/"

    print("Here you can see list of files that contain data from device\n")
    # wyświetlenie zawartości całego folderu z plikami testowymi
    for file in os.listdir(file_directory):
        if file.endswith(".txt"):
            print(os.path.join(file_directory, file))
    print()

    file_name = input("Please, enter name of file with extension: \n")

    # ścieżka do pliku
    path = file_directory + file_name
    # zmienna, która mówi czy wprowadzony przez użytkownika plik istnieje
    is_file = os.path.isfile(path)

    # jeśli istnieje to czytaj plik
    if is_file:
        read_file(path)
    # w przeciwnym wypadku poproś o wprowadzeniu nowych danych lub zakończ program
    else:
        print("This is not a valid file name. Do you want to try again?\n")
        print("Press 'y' to enter a new name of file. \n", end='')
        print("Press 'e' if you want to hava a break for a cup of tea and exit a program. \n")
        choice = input()
        print('\n')
        menu(choice)


def read_file(path):
    # liczba column w pliku tekstowym
    number_of_variables = 9


    with open(path, 'r') as reader:
        for line in reader:
            list_string = list(line.split('\t'))
            # chcemy zostawić godzinę i dane kalendarzowe w formacie string
            list_string_t = list_string[2:9]
            list_float = [float(x) for x in list_string_t]
            # jeśli wykryli większą lub mniejszę liczbę słów w wierszu pliku to rzuć exception
            if len(list_string) > number_of_variables or len(list_string) < number_of_variables:
                raise Exception("You've just opened corrupted or wrong file")
            else:
                calendar.append(list_string[0])
                timer.append(list_string[1])
                acc_x.append(list_float[0])
                acc_y.append(list_float[1])
                acc_z.append(list_float[2])
                gyro_x.append(list_float[3])
                gyro_y.append(list_float[4])
                gyro_z.append(list_float[5])
                counter.append(list_float[6])
    # po wczytaniu plik zacznij analizę
    analysis_UI(calendar, timer, acc_x, acc_y, acc_z, counter)


# funkcja inicjalizująca zakończenie programu
def stop():
    clear_console()
    print("-----------------------------------------------------------------------------------------------------------")
    print("                                        THANK YOU, SAYONARA!                                               ")
    print("-----------------------------------------------------------------------------------------------------------")
    exit()


# odpowiednik konstrukcji switch w python
def menu(argument):
    switcher = {
        'y': start,         # nazwa funkcji która zostanie wywołana gdy użykownik naciśni klawiszę 'y'
        'e': stop,          # nazwa funkcji która zostanie wywołana gdy użykownik naciśni klawiszę 'e'
    }
    # Get the function from switcher dictionary
    func = switcher.get(argument, lambda: "Invalid data")
    # Execute the function
    print(func())


def analysis_UI(calendar, timer, acc_x, acc_y, acc_z, counter):
        print("Data was recorded in the time interval from", calendar[0], " at ", timer[0], " to ",
              calendar[len(calendar)-1], " at ", timer[len(timer)-1], "\n")

        # print("Enter the day of month from which you want to start analysis: ")
        # day_begin = is_number()
        # print("Enter the number of month from which you want to start analysis: ")
        # month_begin = is_number()
        # print("Enter the year from which you want to start analysis: ")
        # year_begin = is_number()
        print("Enter the hour from which you want to start analysis: ")
        hour_begin = is_number()
        print("Enter minute from which you want to start analysis: ")
        minute_begin = is_number()
        print("Enter seconds from which you want to start analysis: ")
        seconds_begin = is_number()

        print()
        print("START TIME: ", hour_begin, ":", minute_begin, ":", seconds_begin, sep='')
        print()

        print("Data was recorded in the time interval from", calendar[0], " at ", timer[0], " to ",
              calendar[len(calendar) - 1], " at ", timer[len(timer) - 1], "\n")

        # print("Enter stop day of month: ")
        # day_stop = is_number()
        # print("Enter stop number of month: ")
        # month_stop = is_number()
        # print("Enter stop year: ")
        # year_stop = is_number()
        print("Enter stop hour: ")
        hour_stop = is_number()
        print("Enter stop minute: ")
        minute_stop = is_number()
        print("Enter stop seconds: ")
        seconds_stop = is_number()

        print()
        print("STOP TIME: ", hour_stop, ":", minute_stop, ":", seconds_stop, sep='')
        print()

        analysis(calendar, timer, acc_x, acc_y, acc_z, counter, hour_stop, minute_stop, seconds_stop, hour_begin, minute_begin, seconds_begin)


def analysis(calendar_raw, timer_raw, acc_x, acc_y, acc_z, counter, hour_stop, minute_stop, seconds_stop, hour_begin, minute_begin, seconds_begin):
    timer = []
    for d in timer_raw:
        timer.append(remove_delimiters('.', d))

    timer_stop = concatenate_data_integer(hour_stop, minute_stop, seconds_stop)
    timer_start = concatenate_data_integer(hour_begin, minute_begin, seconds_begin)

    # sprawdzenie czy użytkownik wprowadził poprawny przedział czasowy,
    # jeśli jednak nie - to proszony zostaje wprowadzić dane jeszcze raz
    if str(timer_stop) not in timer or str(timer_start) not in timer:
        clear_console()
        print("Data you've provided is wrong. Check correct time interval. Please repeat again.")
        print()
        analysis_UI(calendar_raw, timer_raw, acc_x, acc_y, acc_z, counter)
    else:
        clear_console()
        print("ANALYSIS WAS STARTED...")
        print("START TIME: ", hour_begin, ":", minute_begin, ":", seconds_begin, sep='')
        print("STOP TIME: ", hour_stop, ":", minute_stop, ":", seconds_stop, "\n", sep='')
        print("INFORMATION: \n")
        # Zakładamy na razie, że zmieniony zostanie tylko czas
        index_pos_start = timer.index(str(timer_start))
        # Get last index of item in list
        index_pos_stop = len(timer) - timer[::-1].index(str(timer_stop)) - 1

        # Tylko dane, które potrzebujemy dla wyświetlania
        acc_x_cut = acc_x[index_pos_start:index_pos_stop]
        acc_y_cut = acc_y[index_pos_start:index_pos_stop]
        acc_z_cut = acc_z[index_pos_start:index_pos_stop]
        # blok kodu reprezentujący sprawdzenie, czy pacjent umarł podczas badania
        if 1000 in counter[index_pos_start:index_pos_stop]:
            # Szukamy indeksu w liczniku, kiedy po raz pierwszy wystąpił sygnał śmierci
            index_died = counter.index(1000, index_pos_start, index_pos_stop)
            print("The patient died at", timer_raw[index_died])
        else:
            print("The patient is still alive.")
        print()
        acc_x_filtered = filter_data(acc_x_cut)
        acc_y_filtered = filter_data(acc_y_cut)
        peaks_x = find_peaks_custom(acc_x_filtered)
        peaks_y = find_peaks_custom(acc_y_filtered)
        # print(peaks_x)
        time = calculate_time(hour_begin, hour_stop, minute_begin, minute_stop, seconds_begin, seconds_stop)
        print(time)
        breaths_per_minute_x = average_breath_per_minute(peaks_x, time)
        breaths_per_minute_y = average_breath_per_minute(peaks_y, time)
        print("Average breaths per minute from X axis:", breaths_per_minute_x)
        print("Average breaths per minute from Y axis:", breaths_per_minute_y)
        print()
        plot_graphs(acc_x_cut, acc_y_cut, acc_z_cut, acc_x_filtered, acc_y_filtered, peaks_x, peaks_y)
        choice = input("What do you want to do next? To continue work press 'y', if you've already sick of it, please, press 'e': ")
        menu(choice)


def plot_graphs(acc_x, acc_y, acc_z, acc_x_filtered, acc_y_filtered, peaks_x, peaks_y):
    # rysowanie X osi
    f_1 = plt.figure(1, figsize=[13, 4.8])
    # Dodanie subplotów do naszego plotu:)
    ax_1 = f_1.add_subplot(121)
    ax_2 = f_1.add_subplot(122)

    # Subplot 1 of acc_x axis
    ax_1.plot(np.arange(len(acc_x)), acc_x, linewidth=0.7)
    # Title subplotu
    ax_1.set_title("Unfiltered data")
    ax_1.set_xlabel("Samples")
    ax_1.set_ylabel("Raw data")
    # Subplot 2 of acc_x axis
    ax_2.plot(np.arange(len(acc_x_filtered)), acc_x_filtered, 'r', linewidth=0.7)
    ax_2.axhline(y=0, color='k', linewidth=0.5, linestyle='--')
    ax_2.plot(peaks_x, acc_x_filtered[peaks_x], "v")
    # Title subplotu
    ax_2.set_title("Filtered and normalized  data")
    ax_2.set_xlabel("Samples")
    ax_2.set_ylabel("Normalized filtered data")
    ax_2.legend(['Data', 'Zero-level', 'Peaks'])
    # Title całego plotu
    f_1.suptitle("X-axis")
    # Display
    f_1.show()

    # rysowanie Y osi
    f_2 = plt.figure(2, figsize=[13, 4.8])
    # Dodanie subplotów do naszego plotu:)
    ax_1 = f_2.add_subplot(121)
    ax_2 = f_2.add_subplot(122)
    # Subplot 1 of acc_x axis
    ax_1.plot(np.arange(len(acc_y)), acc_y, linewidth=0.7)
    # Title subplotu
    ax_1.set_title("Unfiltered data")
    ax_1.set_xlabel("Samples")
    ax_1.set_ylabel("Raw data")
    # Subplot 2 of acc_x axis
    ax_2.plot(np.arange(len(acc_y_filtered)), acc_y_filtered, 'r', linewidth=0.7)
    ax_2.axhline(y=0, color='k', linewidth=0.5, linestyle='--')
    ax_2.plot(peaks_y, acc_y_filtered[peaks_y], "v")
    # Title subplotu
    ax_2.set_title("Filtered and normalized  data")
    ax_2.legend(['Data', 'Zero-level', 'Peaks'])
    ax_2.set_xlabel("Samples")
    ax_2.set_ylabel("Normalized filtered data")
    # Title całego plotu
    f_2.suptitle("Y-axis")
    # Display
    f_2.show()

    plt.figure(3)
    plt.plot(np.arange(len(acc_z)), acc_z, linewidth=0.7)
    plt.suptitle("Z-axis")
    plt.xlabel("Sample")
    plt.ylabel("Raw data")
    # Display
    plt.show()


# ile czasu zajmieje przedział wybrany przez użytkownika
def calculate_time(hour_begin, hour_stop, minute_begin, minute_stop, seconds_begin, seconds_stop):
    hour_diff = hour_stop - hour_begin
    seconds_result = hour_diff*60*60;

    if minute_stop > minute_begin and seconds_stop < seconds_begin:
        minute_diff = minute_stop - minute_begin - 1
    elif minute_stop > minute_begin and seconds_stop > seconds_begin:
        minute_diff = minute_stop - minute_begin
    elif minute_stop == minute_begin:
        minute_diff = 0
    else:
        temp = 60 - minute_begin
        minute_diff = temp + minute_stop

    seconds_result = seconds_result + minute_diff*60;

    if seconds_stop > seconds_begin or seconds_stop == seconds_begin:
        seconds_diff = seconds_stop - seconds_begin
    else:
        temp = 60 - seconds_begin;
        seconds_diff = temp + seconds_stop;

    seconds_result = seconds_result + seconds_diff
    return seconds_result


def average_breath_per_minute(peaks, time):
    breath_per_minute = ceil((len(peaks)*60)/time)
    return breath_per_minute


# Ze względu na to, że otrzymany przebieg nie jest idealnie wygładzony przez
# filtr, musimy usunąć zbędne maksyma lokalne, które znajdują się blisko siebie
def find_peaks_custom(some_peaks):
    peaks, _ = find_peaks(some_peaks, height=0)
    # print(peaks)
    peaks = list(peaks)
    for i in range(len(peaks)-2, -1, -1):
        # średnio szcztyty leżą w zakresie 100 "próbek"
        if abs(peaks[i] - peaks[i + 1]) < 20:
            peaks.pop(i + 1)
    return peaks

def filter_data(some_array):
    normalized_array = stats.zscore(some_array)
    filtered_array = savgol_filter(normalized_array, 101, 5)
    return filtered_array

# funkcja, dzięki której sklejamy wprowadzone przez użytkownika dane odnośnie godziny i daty
def concatenate_data_integer(*args):
    product = ""
    for a in args:
        product += str(a)
    product = int(product)
    return product


# funkcja, która nic nie będzie zwracać póki użytkownik nie wprowadzi typ integer
def is_number():
    while True:
        try:
            num = int(input())
            break
        except ValueError:
            print("Please input integer only...")
            continue
    return num


# usuwamy separatory w string
def remove_delimiters (delimiter, s):
    ind = s.find(delimiter)
    while ind != -1:
        s = s[:ind] + s[ind+1:]
        ind = s.find(delimiter)

    return ' '.join(s.split())

# "MAIN" body of our program
clear_console()
print("-----------------------------------------------------------------------------------------------------------")
print("                                           IBREATHE v1.1                                                   ")
print("-----------------------------------------------------------------------------------------------------------")
print("Dear, User! Welcome to our UI application of a brand-new revolutionary device:")
print();
print("                                            IBREATH                                                        ")
print();
print("What do you want to do now?")
print("Press 'y' to start analyses. \n", end='')
print("Press 'e' if you've just opened wrong application. \n")
choice = input()
print('\n')
menu(choice)


