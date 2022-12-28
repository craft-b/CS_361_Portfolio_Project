# CS_361_Portfolio_Project
Person Generator Microservice using Tkinter GUI

This project contains microservices for person generator (refactored version) and life generator.  It also contains 
the original person generator file(generator.py), which isn't used in the execution.

Each microservice can operate independently, while both can communicate asynchronously through a set of queues.

RabbitMQ is the host of said queues that store the messages (from either side) for retreival.


To use:

State csv files are required 

amazon_co-ecommerce_sample csv file is required 


Running this code in terminal with GUI: 

`py ppl-generator_consumer_refactored.py` (for Person Generator)
`py life-generator_producer.py` (for Life Generator)


Or with file:

`py ppl-generator_consumer_refactored.py input_ppl.csv` (for Person Generator)
`py life-generator_producer.py input.csv` (for Life Generator)


Program and files should be saved to C: directory using gui folder (i.e. "c:/gui/" directory) 
state.csv files and input.csv file will need to be saved in the gui folder with the program 


