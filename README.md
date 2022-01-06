# Wordle Solver

# Installation
Install the following onto your computer:
1. Python 3.10.x
   1. [Download Page](https://www.python.org/downloads/)
2. Run ```pip install -r requirements.txt```

# Instructions
To run the wordle solver, run ```python wordle_solver.py```. After running, perform the following steps:

1. Insert given word to [Wordle site](https://www.powerlanguage.co.uk/wordle/).
2. Input the result from the site in the following format:
   1Grey letters = 0
   2Yellow letters = 1
   3Green letters = 2
3. Repeat this process with each newly given word until the word is found or no more rounds remain.

## Example
Winning Word: ***sight***
```commandline
What was the result of stoae?
0=Grey
1=Yellow
2=Green
Word: stoae
 Ans: 20000

What was the result of shist?
0=Grey
1=Yellow
2=Green
Word: shist
 Ans: 21102

What was the result of sight?
0=Grey
1=Yellow
2=Green
Word: sight
 Ans: 22222

SUCCESS!
```