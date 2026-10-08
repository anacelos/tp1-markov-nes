


def interval_histogram(sequences):
    """
    Return a dict mapping each interval to its proportion over all sequences.
    """ 

    counts = {}
    total = 0
    for each_seq in sequences:
        for each_x in each_seq:
            counts[each_x] = counts.get(each_x , 0) + 1
            total += 1
    hist = {}
    for each_int, each_x in counts.items():
        hist[each_int] = each_x / total

    return hist 

def tv_distance(h1, h2):
    """
    Return the total variation distance between two histograms (0 = identical, 
    1 = no overlap).
    """

    h1_U_h2 = set(h1) | set(h2)
    sume = 0
    for each_key in h1_U_h2:
        val_1 = h1.get(each_key, 0)
        val_2 = h2.get(each_key, 0)
        sume += (abs(val_2 - val_1))

    return sume / 2

def japaneseness(h, h_nes, h_js):
    """
    Return how close a histogram is to JSMel rather than NES (0 = NES, 
    1 = JSMel).
    """

    d_nes = tv_distance(h, h_nes)
    d_js = tv_distance(h, h_js)

    return d_nes / (d_nes + d_js)