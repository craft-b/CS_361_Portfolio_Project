# CS_361_Portfolio_Project
Person Generator Desktop App using Tkinter GUI

This project contains a microservice (person generator) that outputs a given number of street addresses for the selected
state  and a microservice (life generator) that outputs the top toys for a selected category. “Top” means
highest rating combined with highest number of reviews.  

Each microservice can operate independently and can communicate asynchronously through a set of queues.

RabbitMQ is the host of said queues that store the messages (from either side) for retreival.


To use:

Create a 'gui' folder on the C: drive.
Download the 'ppl-generator_consumer_refactored.py' and 'life-generator_producer.py' program files to the 'gui' folder.
Download the 'input_ppl.csv' and 'input.csv' files to the 'gui' folder.

State csv data files are required for the person generator.  They should be downloaded 
from https://www.kaggle.com/datasets/openaddresses/openaddresses-us-west and saved to the 'gui' folder

An amazon_co-ecommerce_sample csv dataset is required for the life generator.  It should be downloaded
from https://www.kaggle.com/datasets/PromptCloudHQ/toy-products-on-amazon and saved to the 'gui' folder


Running this code in terminal with GUI: 

`py ppl-generator_consumer_refactored.py` (for Person Generator)
`py life-generator_producer.py` (for Life Generator)


Or with input file:

`py ppl-generator_consumer_refactored.py input_ppl.csv` (for Person Generator)
`py life-generator_producer.py input.csv` (for Life Generator)


All programs and files should be saved to C: directory using a gui folder (i.e. "c:/gui/" directory) 


