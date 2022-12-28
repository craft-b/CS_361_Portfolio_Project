# ------------------------------------------------------------------------------
# Program: life-generatory.py
# Class: CS361: Sprint 3 Assignment - Life Generator Project
# Date: Feb. 14, 2021
# Name: Jay Chaudhry
# ------------------------------------------------------------------------------
import sys
import tkinter as tk
from csv import reader, writer, DictReader, DictWriter
from tkinter import ttk

import os
import pandas as pd
import pika
import sys

def send_message_to_host():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='life_gen')

    file = 'c:/gui/output.csv'
    input_data = pd.read_csv(file, low_memory=False)
    df = pd.DataFrame(input_data, columns=['input_number_to_generate']).values.tolist()
    num_of_items = str(df[0][0])

    channel.basic_publish(exchange='', routing_key='life_gen', body=str(num_of_items))
    print(" [x] The message was sent from Life Generator.")
    connection.close()


def get_messages_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='ppl_gen')

    def callback(ch, method, properties, body):
        print(" [x] The message that Life Generator received was %r" % body.decode())

    channel.basic_consume(queue='ppl_gen', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.start_consuming()


# If input.csv file is used
if len(sys.argv) > 1:
    # print(sys.argv[1])
    item = ""
    cat = ""
    num1 = 0
    with open(sys.argv[1], 'r') as file:
        # contents = file.read()
        contents = reader(file)
        data = list(contents)
        item = data[1][0]
        cat = data[1][1]
        num1 = int(data[1][2])

        print(f'Contents: {item}, {cat}, {num1}')

    # launch results page of GUI
    def go_to_results(sort5, num1):
        root = tk.Tk()  # creating main window as a tk object
        root.geometry("550x550")
        root.resizable(0, 0)
        root.title("Life Generator - Producer Microservice")
        root.configure(background='#bb9457')
        root.pack_propagate(False)

        results_page = tk.Frame(root, bg="#bb9457")
        #results_page.pack(fill='both', expand=1)
        results_page.place(height=480, width=500, relx=0.04, rely=0.04)

        nav = tk.Frame(root, bg='white')
        nav.pack(side="bottom", expand=1)

        close_btn = tk.Button(root, text="Close", bg="#bb9457", fg="white", command=lambda: root.destroy())
        close_btn.place(relx=0.45, rely=0.92)

        scroll = ttk.Scrollbar(results_page)
        scroll.pack(side='right', fill='y', expand=False)
        scroll2 = ttk.Scrollbar(results_page, orient=tk.HORIZONTAL)
        scroll2.pack(side='bottom', fill='x', expand=False)

        # create treeview list
        tree = ttk.Treeview(results_page, columns=('number', 'input_item_type', 'input_item_category',
                                                   'input_number_to_generate', 'input_item_name', 'output_item_rating',
                                                   'output_item_num_reviews'))
        style = ttk.Style(results_page)
        style.configure('Treeview', rowheight=25)
        tree.heading('#0', text='number')
        # tree.heading('#1', text="uniq_id")
        tree.heading('#1', text="input_item_type")
        tree.heading('#2', text="input_item_category")
        tree.heading('#3', text="input_number_to_generate")
        tree.heading('#4', text='input_item_name')
        tree.heading('#5', text='output_item_rating')
        tree.heading('#6', text='output_item_num_reviews')

        tree.column('#0', width=80)
        # tree.column('#1', width=300)
        tree.column('#1', width=150)
        tree.column('#2', width=200)
        tree.column('#3', width=250)
        tree.column('#4', width=500)
        tree.column('#5', width=200)
        tree.column('#6', width=200)

        tree.pack(fill='both', expand=1)
        treeview = tree

        # insert a new row in treeview for every item in sorted toy list
        count = 1
        for row in sort5:
            new_cat = row[8].split(" > ")
            treeview.insert('', 'end', text=count, values=("toys", new_cat[0], num1, row[1], row[7], row[5]))
            count += 1

        # print(sort5)
        scroll.config(command=tree.yview)
        scroll2.config(command=tree.xview)

        root.mainloop()  # run GUI


    # create list of all toys found in a single category
    toy_list = []
    with open("amazon_co-ecommerce_sample.csv", encoding="ISO-8859-1") as file:
        csv_reader = reader(file)
        new_list = []
        for row in csv_reader:
            if cat in row[8]:
                toy_list.append(row)

    # first sort: sort all toys in list by unique id number
    # replace illegal or missing chars
    sort1 = sorted(toy_list, key=lambda x: x[0])
    for row in sort1:
        if ',' in row[5]:
            row[5] = row[5].replace(',', '')
        if row[5] == "":
            row[5] = 0
            row[7] = "0.0 out of 5 stars"

    # second sort: sort toy list by the number of ratings (high/low)
    sort2 = sorted(sort1, key=lambda x: int(x[5]), reverse=True)

    # calculate length of new toy list
    top_to_gen = num1 * 10

    # add to new list while there are items in 2nd sorted toy list
    count3 = 0
    sort3 = []
    while count3 < len(sort2) and count3 < top_to_gen:
        sort3.append(sort2[count3])
        count3 += 1

    # sort x*10 list by unique id number
    sort4 = sorted(sort3, key=lambda x: x[0])

    # parse ratings string and select first index from list, cast to float and place at end of list
    list1 = ''
    for row in sort4:
        list1 = row[7].split()
        # print(list1)
        row.append(float(list1[0]))

    # final sort by newly appended last element in list (avg. review float)
    sort5 = sorted(sort4, key=lambda x: x[-1], reverse=True)[:num1]

    # display results page
    go_to_results(sort5, num1)

    # write results to output.csv
    with open('output.csv', 'w') as file:
        fnames = ['input_item_type', 'input_item_category', 'input_number_to_generate',
                  'output_item_name', 'output_item_rating', 'output_item_num_reviews']
        csv_writer = DictWriter(file, fieldnames=fnames)
        csv_writer.writeheader()
        for row in sort5:
            short_cat = row[8].split(" > ")
            csv_writer.writerow(
                {'input_item_type': 'toys', 'input_item_category': short_cat[0], 'input_number_to_generate': num1,
                 'output_item_name': row[1], 'output_item_rating': row[7], 'output_item_num_reviews': row[5]})


# if no input.csv launch GUI start screen
else:
    root = tk.Tk()  # creating main window as a tk object
    root.geometry("550x550")
    root.resizable(0, 0)
    root.title("Life Generator - Producer Microservice")
    root.configure(background='#bb9457')
    root.pack_propagate(False)


    # create frames and elements
    home_frame = tk.Frame(root, bg='#bb9457')
    home_frame.pack(fill='both', expand=1)
    results_page = tk.Frame(root, bg="#bb9457")
    nav = tk.Frame(root, bg='white')
    scroll = ttk.Scrollbar(results_page)
    scroll.pack(side='right', fill='y', expand=False)
    scroll2 = ttk.Scrollbar(results_page, orient=tk.HORIZONTAL)
    scroll2.pack(side='bottom', fill='x', expand=False)
    close_btn = tk.Button(root, text="Close", bg="#bb9457", fg="white", command=lambda: root.destroy())
    close_btn.place(relx=0.45, rely=0.87)


    # -----------------------------------------------------------------------------
    # Name: go_to_results
    # Procedure: Renders results page
    # -----------------------------------------------------------------------------
    def go_to_results(sort5, num1):
        home_frame.forget()
        results_page.place(height=445, width=500, relx=0.04, rely=0.04)
        nav.pack(side="bottom")

        # create treeview list
        tree = ttk.Treeview(results_page, columns=('number', 'input_item_type', 'input_item_category',
                                                   'input_number_to_generate', 'input_item_name', 'output_item_rating',
                                                   'output_item_num_reviews'))
        style = ttk.Style(results_page)
        style.configure('Treeview', rowheight=25)
        tree.heading('#0', text='number')
        # tree.heading('#1', text="uniq_id")
        tree.heading('#1', text="input_item_type")
        tree.heading('#2', text="input_item_category")
        tree.heading('#3', text="input_number_to_generate")
        tree.heading('#4', text='input_item_name')
        tree.heading('#5', text='output_item_rating')
        tree.heading('#6', text='output_item_num_reviews')

        tree.column('#0', width=80)
        # tree.column('#1', width=300)
        tree.column('#1', width=100)
        tree.column('#2', width=150)
        tree.column('#3', width=150)
        tree.column('#4', width=300)
        tree.column('#5', width=150)
        tree.column('#6', width=150)

        tree.pack(fill='both', expand=1)
        treeview = tree

        # insert a new row in treeview for every item in sorted toy list
        count = 1
        for row in sort5:
            new_cat = row[8].split(" > ")
            treeview.insert('', 'end', text=count, values=("toys", new_cat[0], num1, row[1], row[7], row[5]))
            count += 1

        scroll.config(command=tree.yview)
        scroll2.config(command=tree.xview)


    # separated all list categories from sub-categories
    with open("amazon_co-ecommerce_sample.csv", encoding="ISO-8859-1") as file:
        csv_reader = reader(file)
        new_list = []
        for row in csv_reader:
            new_row = row[8].split(" > ")
            if new_row not in new_list:
                new_list.append(new_row)

    # create set to ensure no duplicate categories
    new_set = {x[0] for x in new_list}  # set comprehension ensures no duplicate categories
    new_list3 = list(new_set)  # place categories in temp list
    new_list3.sort()  # sort categories alphabetically

    # create a keyword list used to filter list of total categories
    categories = ["Toy", "Hobbies", "Jigsaws", "Games", "Dolls", "Play", "Characters", "Arts", "Puppet"]

    # filter out non-toy categories from category list to use in drop-down
    cat_list = []
    for list in new_list3:
        for cat in categories:
            if cat in list:
                # if "Toy" in list or "Hobbies" in list or "Jigsaws" in list or "Games" in list or "Dolls" in list or "Characters" in list or "Arts" in list:
                cat_list.append(list)
                # print(list)


    # options = cat_list

    # ------------------------------------------------------------------------------
    # Name: generate_list
    # Procedure: To create a list of top X toys from Y categories
    # ------------------------------------------------------------------------------
    def generate_list():
        cat = selected_weekday.get()
        num1 = var1.get()
        print(f'The chosen category is: {cat} and the number is: {num1}')

        toy_list = []
        with open("amazon_co-ecommerce_sample.csv", encoding="ISO-8859-1") as file:
            csv_reader = reader(file)
            # data = list(csv_reader)
            # new_list = []
            for row in csv_reader:
                # print(f'{row[0]}: number or reviews {row[4]}: category {row[8]}'
                if cat in row[8]:
                    toy_list.append(row)

        # print(toy_list[10])
        sort1 = sorted(toy_list, key=lambda x: x[0])
        for row in sort1:
            if ',' in row[5]:
                row[5] = row[5].replace(',', '')
            if row[5] == "":
                row[5] = 0
                row[7] = "0.0 out of 5 stars"

        sort2 = sorted(sort1, key=lambda x: int(x[5]), reverse=True)

        top_to_gen = num1 * 10  # numbers to take from sorted by reviews

        # add to new list while there are items in 2nd sorted toy list
        count3 = 0
        sort3 = []
        while (count3 < len(sort2) and count3 < top_to_gen):
            sort3.append(sort2[count3])
            count3 += 1

        # sort x*10 list by unique id number
        # count4 = 0
        sort4 = sorted(sort3, key=lambda x: x[0])

        # parse ratings string and select first index from list, cast to float and place at end of list
        list1 = ''
        for row in sort4:
            list1 = row[7].split()
            # print(list1)
            row.append(float(list1[0]))

        # final sort by newly appended last element in list (avg. review float)
        sort5 = sorted(sort4, key=lambda x: x[-1], reverse=True)[:num1]

        # write results to output.csv
        with open('output.csv', 'w') as file:
            fnames = ['input_item_type', 'input_item_category', 'input_number_to_generate',
                      'output_item_name', 'output_item_rating', 'output_item_num_reviews']
            csv_writer = DictWriter(file, fieldnames=fnames)
            csv_writer.writeheader()
            for row in sort5:
                short_cat = row[8].split(" > ")
                csv_writer.writerow(
                    {'input_item_type': 'toys', 'input_item_category': short_cat[0], 'input_number_to_generate': num1,
                     'output_item_name': row[1], 'output_item_rating': row[7], 'output_item_num_reviews': row[5]})

        # display results page
        go_to_results(sort5, num1)


    # create drop-down menu
    var1 = tk.IntVar()
    selected_weekday = tk.StringVar()
    drop = ttk.Combobox(home_frame, textvariable=selected_weekday)
    drop["values"] = cat_list
    drop["state"] = "readonly"  # "normal"
    drop.set('Choose a Category')
    drop.place(relx=0.35, rely=0.35, relwidth=0.3, relheight=0.05)
   # drop.pack()


    # create textfield elements
    results_label = tk.Label(home_frame, text="Producer", font=("Courier", 25), bg='#bb9457')
    results_label.place(relx=0.30, rely=0.025, relwidth=0.4, relheight=0.3)

    # create textfield elements
    results_label = tk.Label(home_frame, text="Number of Results: ", bg='#bb9457')
    results_label.place(x=180, y=250)
    entry = tk.Entry(home_frame, textvariable=var1)
    entry.place(x=310, y=250, width=50)

    # create button element to generate list
    generate_btn = tk.Button(home_frame, text="Generate List", bg='#bb9457', fg='white', width=15, command=generate_list)
    generate_btn.place(x=220, y=350)

    # run GUI interface
    root.mainloop()

if __name__ == '__main__':
    try:
        send_message_to_host()
        get_messages_from_queue()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
