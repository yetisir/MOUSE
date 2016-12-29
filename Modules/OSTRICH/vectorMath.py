#!/usr/bin/env python3
import math
def process1(lista):
    import numbers
    if isinstance(lista, numbers.Real):
        lista = (lista, )
    return lista
def process2(lista, listb):
    import numbers
    if isinstance(lista, numbers.Real):
        lista = (lista, )*len(listb)
    if isinstance(listb, numbers.Real):
        listb = (listb, )*len(lista)
    return lista, listb
def multiply(lista, listb):
    lista, listb = process2(lista, listb)
    return [a*b for a,b in zip(lista,listb)]
def divide(lista, listb):
    lista, listb = process2(lista, listb)
    return [a/float(b) if b != 0 else float('NaN') for a,b in zip(lista,listb)]
def add(lista, listb):
    lista, listb = process2(lista, listb)
    return [a+b for a,b in zip(lista,listb)]
def subtract(lista, listb):
    lista, listb = process2(lista, listb)
    return [a-b for a,b in zip(lista,listb)]
def exp(lista):
    import math
    lista = process1(lista)
    return [math.exp(x) for x in lista]
def log(lista):
    import math
    lista = process1(lista)
    return [math.log(x) if x > 0 else float('NaN') for x in lista]
def power(lista, listb):
    import math
    lista, listb = process2(lista, listb)
    return [a**b for a, b in zip(lista,listb)]
def fWrite(stuff):
    with open('log.txt', 'a') as f:
        f.write(str(stuff)+'\n')
        
        

        
   
