#!/bin/bash

while true
do
	pkill -f python2
	python2 /home/python-scripts/datagen.py 1&
	python2 /home/python-scripts/datagen.py 2&
	python2 /home/python-scripts/datagen.py 3&
	python2 /home/python-scripts/datagen.py 4&
	python2 /home/python-scripts/datagen.py 5&
	python2 /home/python-scripts/datagen.py 6&
	python2 /home/python-scripts/datagen.py 7&
	python2 /home/python-scripts/datagen.py 8&
	python2 /home/python-scripts/datagen.py 9&
	python2 /home/python-scripts/datagen.py 10&
	python2 /home/python-scripts/datagen.py 11&
	python2 /home/python-scripts/datagen.py 12&
	python2 /home/python-scripts/datagen.py 13&
	python2 /home/python-scripts/datagen.py 14&
	python2 /home/python-scripts/datagen.py 15&
	python2 /home/python-scripts/datagen.py 16&
	sleep 300
done
