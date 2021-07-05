
NI6602_PFI = {
    "ctr0": {"src": "PFI39", "gate": "PFI38", "out": "PFI36", "aux": "PFI37"},
    "ctr1": {"src": "PFI35", "gate": "PFI34", "out": "PFI32", "aux": "PFI33"},
    "ctr2": {"src": "PFI31", "gate": "PFI30", "out": "PFI28", "aux": "PFI29"},
    "ctr3": {"src": "PFI27", "gate": "PFI26", "out": "PFI24", "aux": "PFI25"},
    "ctr4": {"src": "PFI23", "gate": "PFI22", "out": "PFI20", "aux": "PFI21"},
    "ctr5": {"src": "PFI19", "gate": "PFI18", "out": "PFI16", "aux": "PFI17"},
    "ctr6": {"src": "PFI15", "gate": "PFI14", "out": "PFI12", "aux": "PFI13"},
    "ctr7": {"src": "PFI11", "gate": "PFI10", "out": "PFI8",  "aux": "PFI9"}}


def get_pfi(input):
    if 'pfi' in input.lower() or 'rtsi' in input.lower():
        return input
    try:
        _, card, counter, terminal = input.split('/')
    except Exception:
        raise ValueError('Wrong definition. E.g.: /Dev1/ctr0/gate')

    pfi = NI6602_PFI[counter][terminal]
    return f'/{card}/{pfi}'
