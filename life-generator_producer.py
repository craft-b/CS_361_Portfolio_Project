# ------------------------------------------------------------------------------
# Program: life-generator_producer.py
# Class: CS361: Sprint 3 Assignment - Life Generator Project
# Date: Feb. 14, 2021
# Name: Jay Chaudhry
# ------------------------------------------------------------------------------
import os
import sys
import tkinter as tk
from csv import reader, DictWriter
from tkinter import ttk

import pandas as pd
import pika

# Data directory: set DATA_DIR env variable to override (defaults to script's directory)
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
AMAZON_CSV = os.path.join(DATA_DIR, 'amazon_co-ecommerce_sample.csv')


def send_message_to_host():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='life_gen')

    output_file = os.path.join(DATA_DIR, 'output.csv')
    input_data = pd.read_csv(output_file, low_memory=False)
    num_of_items = str(input_data['input_number_to_generate'].iloc[0])

    channel.basic_publish(exchange='', routing_key='life_gen', body=num_of_items)
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


def rank_toys(cat, num):
    """
    Filters amazon_co-ecommerce_sample.csv by category, ranks by review count
    then average rating, and returns the top `num` results.
    """
    toy_list = []
    with open(AMAZON_CSV, encoding='ISO-8859-1') as f:
        for row in reader(f):
            if cat in row[8]:
                toy_list.append(row)

    # Sort by unique id, clean up review count field
    sort1 = sorted(toy_list, key=lambda x: x[0])
    for row in sort1:
        if ',' in row[5]:
            row[5] = row[5].replace(',', '')
        if row[5] == '':
            row[5] = 0
            row[7] = '0.0 out of 5 stars'

    # Sort by review count (descending), keep top num*10 candidates
    sort2 = sorted(sort1, key=lambda x: int(x[5]), reverse=True)[:num * 10]

    # Re-sort candidates by unique id, then parse and append avg rating float
    sort3 = sorted(sort2, key=lambda x: x[0])
    for row in sort3:
        row.append(float(row[7].split()[0]))

    # Final sort by avg rating (descending), return top num
    return sorted(sort3, key=lambda x: x[-1], reverse=True)[:num]


def build_treeview(parent, scroll_y, scroll_x):
    """Creates and returns a configured Treeview for toy results."""
    cols = ('number', 'input_item_type', 'input_item_category',
            'input_number_to_generate', 'input_item_name',
            'output_item_rating', 'output_item_num_reviews')
    tree = ttk.Treeview(parent, columns=cols)
    ttk.Style(parent).configure('Treeview', rowheight=25)

    tree.heading('#0', text='number')
    tree.heading('#1', text='input_item_type')
    tree.heading('#2', text='input_item_category')
    tree.heading('#3', text='input_number_to_generate')
    tree.heading('#4', text='input_item_name')
    tree.heading('#5', text='output_item_rating')
    tree.heading('#6', text='output_item_num_reviews')

    tree.column('#0', width=80)
    tree.column('#1', width=100)
    tree.column('#2', width=150)
    tree.column('#3', width=150)
    tree.column('#4', width=300)
    tree.column('#5', width=150)
    tree.column('#6', width=150)

    tree.pack(fill='both', expand=1)
    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)
    return tree


def populate_treeview(treeview, results, num):
    for count, row in enumerate(results, start=1):
        category = row[8].split(' > ')[0]
        treeview.insert('', 'end', text=count,
                        values=('toys', category, num, row[1], row[7], row[5]))


def write_output_csv(results, num):
    with open('output.csv', 'w', newline='') as f:
        fnames = ['input_item_type', 'input_item_category', 'input_number_to_generate',
                  'output_item_name', 'output_item_rating', 'output_item_num_reviews']
        csv_writer = DictWriter(f, fieldnames=fnames)
        csv_writer.writeheader()
        for row in results:
            category = row[8].split(' > ')[0]
            csv_writer.writerow({
                'input_item_type': 'toys',
                'input_item_category': category,
                'input_number_to_generate': num,
                'output_item_name': row[1],
                'output_item_rating': row[7],
                'output_item_num_reviews': row[5],
            })


# If input.csv file is provided via command line
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
        data = list(reader(f))
        item = data[1][0]
        cat = data[1][1]
        num1 = int(data[1][2])

    print(f'Contents: {item}, {cat}, {num1}')

    results = rank_toys(cat, num1)
    write_output_csv(results, num1)

    root = tk.Tk()
    root.geometry('550x550')
    root.resizable(0, 0)
    root.title('Life Generator - Producer Microservice')
    root.configure(background='#bb9457')
    root.pack_propagate(False)

    results_page = tk.Frame(root, bg='#bb9457')
    results_page.place(height=480, width=500, relx=0.04, rely=0.04)

    tk.Frame(root, bg='white').pack(side='bottom', expand=1)
    tk.Button(root, text='Close', bg='#bb9457', fg='white',
              command=root.destroy).place(relx=0.45, rely=0.92)

    scroll_y = ttk.Scrollbar(results_page)
    scroll_y.pack(side='right', fill='y', expand=False)
    scroll_x = ttk.Scrollbar(results_page, orient=tk.HORIZONTAL)
    scroll_x.pack(side='bottom', fill='x', expand=False)

    treeview = build_treeview(results_page, scroll_y, scroll_x)
    populate_treeview(treeview, results, num1)

    root.mainloop()

# No input file — launch interactive GUI
else:
    root = tk.Tk()
    root.geometry('550x550')
    root.resizable(0, 0)
    root.title('Life Generator - Producer Microservice')
    root.configure(background='#bb9457')
    root.pack_propagate(False)

    home_frame = tk.Frame(root, bg='#bb9457')
    home_frame.pack(fill='both', expand=1)
    results_page = tk.Frame(root, bg='#bb9457')
    nav = tk.Frame(root, bg='white')

    scroll_y = ttk.Scrollbar(results_page)
    scroll_y.pack(side='right', fill='y', expand=False)
    scroll_x = ttk.Scrollbar(results_page, orient=tk.HORIZONTAL)
    scroll_x.pack(side='bottom', fill='x', expand=False)

    tk.Button(root, text='Close', bg='#bb9457', fg='white',
              command=root.destroy).place(relx=0.45, rely=0.87)

    # Build category list from amazon dataset
    with open(AMAZON_CSV, encoding='ISO-8859-1') as f:
        seen = set()
        all_cats = []
        for row in reader(f):
            top_cat = row[8].split(' > ')[0]
            if top_cat not in seen:
                seen.add(top_cat)
                all_cats.append(top_cat)
    all_cats.sort()

    keywords = ['Toy', 'Hobbies', 'Jigsaws', 'Games', 'Dolls', 'Play', 'Characters', 'Arts', 'Puppet']
    cat_list = [c for c in all_cats if any(k in c for k in keywords)]

    # ------------------------------------------------------------------------------
    # Name: go_to_results
    # Procedure: Renders results page
    # ------------------------------------------------------------------------------
    def go_to_results(results, num):
        home_frame.forget()
        results_page.place(height=445, width=500, relx=0.04, rely=0.04)
        nav.pack(side='bottom')

        treeview = build_treeview(results_page, scroll_y, scroll_x)
        populate_treeview(treeview, results, num)

    # ------------------------------------------------------------------------------
    # Name: generate_list
    # Procedure: To create a list of top X toys from Y categories
    # ------------------------------------------------------------------------------
    def generate_list():
        cat = selected_category.get()
        num = var1.get()
        print(f'The chosen category is: {cat} and the number is: {num}')

        results = rank_toys(cat, num)
        write_output_csv(results, num)
        go_to_results(results, num)

    var1 = tk.IntVar()
    selected_category = tk.StringVar()

    drop = ttk.Combobox(home_frame, textvariable=selected_category)
    drop['values'] = cat_list
    drop['state'] = 'readonly'
    drop.set('Choose a Category')
    drop.place(relx=0.35, rely=0.35, relwidth=0.3, relheight=0.05)

    tk.Label(home_frame, text='Producer', font=('Courier', 25), bg='#bb9457').place(
        relx=0.30, rely=0.025, relwidth=0.4, relheight=0.3)

    tk.Label(home_frame, text='Number of Results: ', bg='#bb9457').place(x=180, y=250)
    tk.Entry(home_frame, textvariable=var1).place(x=310, y=250, width=50)

    tk.Button(home_frame, text='Generate List', bg='#bb9457', fg='white',
              width=15, command=generate_list).place(x=220, y=350)

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
