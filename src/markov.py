"""
Blá
""" 

import numpy as np
import math

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
    Return dist restricted to the allowed states and renormalized to 
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
    index = random_numb.choice(len(states), p = probability)

    return states[index]

def log_prob(model, history, state, order, k = 0.1, vocab = 25):
    """
    Return ln P(state | last order states) with add-k smoothing over a 
    vocabulary of vocab states.
    """

    if len(history) >= order: 
        context = tuple(history[len(history) - order:])
    else:
        context = tuple(history)
    counts = model.get(context, {})
    c = counts.get(state, 0)
    total = sum(counts.values())

    return math.log((c + k) / (total + k * vocab))

def perplexity(model, sequences, order, k = 0.1):
    """
    Return exp(-mean log-probability) of all states in sequences: lower 
    means better prediction.
    """

    sume = 0
    n = 0
    for each_seq in sequences:
        for each_i in range(len(each_seq)):
            sume += log_prob(model, each_seq[:each_i], each_seq[each_i], order, 
                             k)
            n += 1

    return math.exp(-sume / n)

def to_text(seq):
    """
    Return the sequence as text, one character per interval.
    """

    text = ""
    for each_x in seq:
        text += chr(100 + each_x)
    return text

def corpus_text(corpus):
    """
    Return all sequences as one text, separated by '|' so no segment 
    crosses two songs.
    """

    text = []
    for each_s in corpus:
        text.append(to_text(each_s))

    return "|".join(text)

def longest_copy(seq, corpus_txt):
    """
    Return the biggest for the copy.
    """

    s = to_text(seq)
    best = 0
    for each_L in range(1, len(s) + 1):
        found = False
        for each_i in range(len(s) - each_L + 1):
            if s[each_i:each_i + each_L] in corpus_txt:
                found = True
                break
        if not found: 
            break
        best = each_L
    return best

