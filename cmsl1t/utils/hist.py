from cmsl1t.math import cumulative_sum_and_error


def cumulative_hist(hist, suffix='_cumul'):
    h = hist.clone(hist.name + suffix)
    values, errors = cumulative_sum_and_error(hist)
    h.set_content(values)
    h.set_error(errors)
    return h


def normalise_to_collision_rate(hist, collision_rate=4.0e4):
    first_bin = hist.get_bin_content(1)
    if first_bin != 0:
        hist.GetSumw2()
        frac_filled = (2736. / 3564)
        rate_per_event = (collision_rate / first_bin)
        hist.Scale(frac_filled * rate_per_event)
    return hist


def normalise_to_unit_area(histograms):
    for hist in histograms:
        if hist.integral() != 0:
            yield hist / hist.integral()
        else:
            yield hist.Clone()
