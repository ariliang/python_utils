#! /usr/bin/env python3


# create a inversed-generator
def consumer(func):
    def gen_generator(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.send(None)  # send None first for a generator
        return gen
    return gen_generator


@consumer
def gen_display():
    while True:
        n = yield   # inverse generator expression, blocked to receive a value
        if not isinstance(n, int):
            continue
        print(n)


@consumer
def gen_display_square():
    while True:
        n = yield
        if not isinstance(n, int):
            continue
        print(n**2)


# broadcasting
gens = [gen_display(), gen_display_square()]

for i in range(4):
    for gen in gens:
        gen.send(i)
        gen.send(None)  # can be handled
