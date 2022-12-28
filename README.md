# CS_361_Portfolio_Project
Person Generator Desktop App using Tkinter GUI

This project contains microservices for person generator (refactored version) and life generator.  

Each microservice can operate independently and can communicate asynchronously through a set of queues.

RabbitMQ is the host of said queues that store the messages (from either side) for retreival.


To use:

State csv data files are required for the person generator microservice.  They can be downloaded 
from https://www.kaggle.com/datasets/openaddresses/openaddresses-us-west

amazon_co-ecommerce_sample csv file is required 

](https://www.kaggle.com/datasets/openaddresses/openaddresses-us-west)

Running this code in terminal with GUI: 

`py ppl-generator_consumer_refactored.py` (for Person Generator)
`py life-generator_producer.py` (for Life Generator)


Or with file:

`py ppl-generator_consumer_refactored.py input_ppl.csv` (for Person Generator)
`py life-generator_producer.py input.csv` (for Life Generator)


Program and files should be saved to C: directory using gui folder (i.e. "c:/gui/" directory) 
state.csv files and input.csv file will need to be saved in the gui folder with the program 


