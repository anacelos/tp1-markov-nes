"""
Blá
""" 

import numpy as np

# Functions
# ----------------------------------------------------------------------
def train(sequences, max_order):
    """
    Return a dict mapping each context tuple (orders 0..max_order) to
    a dict of next-state counts.
    """

    model = {}
    for seq in sequences:
        for i in range(len(seq)):
            nxt = seq[i]
            for k in range(max_order + 1):
                if (i - k) < 0:
                    continue
                context = tuple(seq[i - k : i])
                if context not in model:
                    model[context] = {}
                model[context][nxt] = model[context].get(nxt, 0) + 1
    
    return model

def distribution(model, history, order):
    """
    Return {state: probability} from the longest context (up to order 
    last states) seen in training, backing off to shorter contexts; {} 
    if none.
    """

    for k in range(order, -1, -1):
        if k > len(history):
            continue
        context = tuple(history[len(history) - k:])
        if context in model:
            counts = model[context]
            total = sum(counts.values())
            probability = {}
            for state, c in counts.items():
                probability[state] = c / total
            return probability
        
    return {}

def mix(dist_a, dist_b, lambd):
    """Return the mixture lambd * dist_a + (1 - lambd) * dist_b over the
    union of their states."""

    probability = {}
    a_U_b = set(dist_a) | set(dist_b)
    for each_state in a_U_b:
        probability[each_state] = lambd * (dist_a.get(each_state, 0)) + (1 - lambd) * \
            (dist_b.get(each_state, 0))
        
    return probability

def constrain(dist, allowed):
    """
    RReturn dist restricted to the allowed states and renormalized to 
    sum 1, or {} if no allowed state has probability.
    """

    probability = {}
    for each_state, prob in dist.items():
        if each_state in allowed:
            probability[each_state] = prob
    total = sum(probability.values())
    if total == 0:
        return {}
    for each_state in probability:
        probability[each_state] = probability[each_state] / total
            
    return probability

def sample(dist, random_numb):
    """
    Return one state drawn from dist using the random generator rng.
    """

    states = list(dist.keys())
    probability = list(dist.values())

    return random_numb.choice(states, p = probability)
