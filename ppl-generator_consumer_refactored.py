#!/usr/bin/env python

# Bobby Craft
# CS 361 
# People Generator
# 2/28/21

from tkinter import *
from tkinter import ttk, filedialog

import os
import pandas as pd
import pika
import sys


def send_messages_to_broker():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='ppl_gen')

    channel.basic_publish(exchange='', routing_key='ppl_gen', body=str(num_of_addresses))
    print(" [x] Person Generator sends a message.")
    connection.close()


def get_messages_from_brokering_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    
    channel.queue_declare(queue='life_gen')

    def callback(ch, method, properties, body):
        print(" [x] The number of items sent from Life Generator was %r" % body.decode())

    channel.basic_consume(queue='life_gen', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages from Life Generator. To exit and launch PPL Generatorpress CTRL+C')

    channel.start_consuming()


def choose_data_creation_method():
    # Launch GUI
    if len(sys.argv) < 2:
        window.mainloop()

    # Else submit csv file
    if sys.argv[1] != '':
        export_input_csv()


def export_input_csv():
    """
    Generates randomized address list from
    given input file. Saves list to directory
    """

    global num_of_addresses

    with open(sys.argv[1], 'r') as input_csv_file:
        input_request = pd.read_csv(input_csv_file, low_memory=False)

        input_state, num_of_addresses = input_request.loc[0, ['input_state', 'input_number_to_generate']]
        input_state = input_state.upper()

        given_state_data_file = f'c:/gui/{input_state}.csv'
        input_data = pd.read_csv(given_state_data_file, low_memory=False)

        out_sampl = input_data.loc[:, ['NUMBER', 'STREET', 'CITY', 'POST CODE']].sample(n=num_of_addresses).astype(str)
        out_sampl['input_state'] = input_state
        out_sampl['input_number_to_generate'] = num_of_addresses
        out_sampl['output_content_type'] = 'street address'
        out_sampl['output_content_value'] = out_sampl['NUMBER'] + ' ' + out_sampl['STREET'] + ',' + ' ' + out_sampl['CITY'] \
        + ' ' + out_sampl['POST CODE'].map(str)

        out_sampl.to_csv('output_people_gen.csv', index=False, header=True)

        send_messages_to_broker()


def create_data_filepath(event):
    """
    Creates path to csv file of
    state selected from pick list
    """

    global state
    global filepath

    state = pick_list_states.get()
    filepath = 'c:/gui/' + state + '.csv'


def create_address_data_set(event):
    global sample
    global num_of_addresses

    num_of_addresses = int(pick_list_num_addresses.get())

    data = pd.read_csv(filepath, low_memory=False)

    # Randomized set of selected number of addresses
    df = pd.DataFrame(data, columns=['NUMBER', 'STREET', 'CITY', 'POSTCODE'])

    sample = df.sample(n=num_of_addresses).astype(str)

    sample['input_state'] = state
    sample['input_number_to_generate'] = num_of_addresses
    sample['output_content_type'] = 'street address'
    sample['output_content_value'] = sample['NUMBER'] + ' ' + sample['STREET'
    ] + ',' + ' ' + sample['CITY'] + ' ' + sample['POSTCODE'].map(str)


def show_addresses_on_gui():
    global input_number_to_generate

    tree.delete(*tree.get_children())

    data_list = sample.values.tolist()

    for i, (NUMBER, STREET, CITY, POSTCODE, input_state, input_number_to_generate,
            output_content_type, output_content_value) in enumerate(data_list, start=1):
        tree.insert('', 'end', values=(NUMBER, STREET, CITY, POSTCODE, input_state,
                                       input_number_to_generate, output_content_type, output_content_value))
    send_messages_to_broker()


def save_results_to_dir():
    export_file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    sample.to_csv(export_file_path, index=False, header=True)


def create_gui_root_window():
    global window

    window = Tk()
    window.pack_propagate(False)
    window.resizable(0, 0)
    window.title('Welcome to the People Generator App')
    window.geometry('550x550')
    window.configure(background='#469d89')


create_gui_root_window()


def create_tree_view_frame():
    global lower_frame
    global frame

    frame = LabelFrame(window, bg='#469d89', text='Input', bd=2)
    frame.place(height=100, width=500, relx=0.04)

    lower_frame = LabelFrame(window, bg='#469d89', text='Street Addresses', bd=2)
    lower_frame.place(height=350, width=500, rely=0.2, relx=0.04)


create_tree_view_frame()


def create_frame_labels():
    global label
    global label2

    label = Label(frame, text='1. Select A State:', bg='#469d89', fg='white')
    label.place(relx=0.137, rely=0.1, relwidth=0.2, relheight=0.3)

    label2 = Label(frame, text='2. Select # of Street Addresses:', bg='#469d89', fg='white')
    label2.place(relx=0.1, rely=0.45, relwidth=0.42, relheight=0.3)


create_frame_labels()


def create_gui_tree_view():
    global tree

    tree = ttk.Treeview(lower_frame, columns=['Number', 'Street', 'City', 'Postal Code'], show='headings')
    tree.place(relx=0, relheight=1, relwidth=1)

    cols = ('Number', 'Street', 'City', 'Postal Code')

    for col in cols:
        tree.heading(col, text=col, anchor='w')

    treescrolly = Scrollbar(lower_frame, orient='vertical', command=tree.yview)
    treescrollx = Scrollbar(lower_frame, orient='horizontal', command=tree.xview)
    tree.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
    treescrollx.pack(side='bottom', fill='x')
    treescrolly.pack(side='right', fill='y')


create_gui_tree_view()


def create_state_pick_list():
    global pick_list_states

    states = ['', 'AK', 'AZ', 'CA', 'CO', 'HI', 'ID', 'MT', 'NM', 'NV', 'OR', 'UT', 'WA', 'WY', ]

    pick_list_states = ttk.Combobox(frame, value=states)
    pick_list_states.current(0)
    pick_list_states.bind('<<ComboboxSelected>>', create_data_filepath)
    pick_list_states.place(relx=0.6, rely=0.2, relwidth=0.13, relheight=0.2)


create_state_pick_list()


def create_num_pick_list():
    global pick_list_num_addresses

    num_of_rows = ['', 1, 20, 40, 60, 80, 100, 200, 400, 600, 800, 1000, 2000, 4000, 8000]

    pick_list_num_addresses = ttk.Combobox(frame, value=num_of_rows)
    pick_list_num_addresses.current(0)
    pick_list_num_addresses.bind('<<ComboboxSelected>>', create_address_data_set)
    pick_list_num_addresses.place(relx=0.6, rely=0.5, relwidth=0.13, relheight=0.2)


create_num_pick_list()


def create_gui_buttons():
    get_address_button = Button(window, text='Get Addresses', bg='#14110f', fg='white',
                                command=show_addresses_on_gui)

    get_address_button.place(relx=0.13, rely=0.85, relwidth=0.2, relheight=0.06)

    close_button = Button(window, text='Close', bg='#bb9457', fg='white', width=15, command=exit)
    close_button.place(relx=0.37, rely=0.85, relwidth=0.2, relheight=0.06)

    save_as_button_csv = Button(window, text='Export CSV', bg='#bb9457', fg='white', width=15,
                                command=lambda: save_results_to_dir())

    save_as_button_csv.place(relx=0.6, rely=0.85, relwidth=0.2, relheight=0.06)


create_gui_buttons()

if __name__ == '__main__':
    try:
        get_messages_from_brokering_queue()
    except KeyboardInterrupt:
        print('Interrupted')
        choose_data_creation_method()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
