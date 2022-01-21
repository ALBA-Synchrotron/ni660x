from nidaqmx.constants import EncoderType, EncoderZIndexPhase, AngleUnits

NI6602_PFI = {
    "ctr0": {"src": "PFI39", "gate": "PFI38", "out": "PFI36", "aux": "PFI37"},
    "ctr1": {"src": "PFI35", "gate": "PFI34", "out": "PFI32", "aux": "PFI33"},
    "ctr2": {"src": "PFI31", "gate": "PFI30", "out": "PFI28", "aux": "PFI29"},
    "ctr3": {"src": "PFI27", "gate": "PFI26", "out": "PFI24", "aux": "PFI25"},
    "ctr4": {"src": "PFI23", "gate": "PFI22", "out": "PFI20", "aux": "PFI21"},
    "ctr5": {"src": "PFI19", "gate": "PFI18", "out": "PFI16", "aux": "PFI17"},
    "ctr6": {"src": "PFI15", "gate": "PFI14", "out": "PFI12", "aux": "PFI13"},
    "ctr7": {"src": "PFI11", "gate": "PFI10", "out": "PFI8",  "aux": "PFI9"}}

NI6602_HUMAN = {
    "PFI39": "ctr0/src",
    "PFI38": "ctr0/gate",
    "PFI37": "ctr0/aux",
    "PFI36": "ctr0/out",
    "PFI35": "ctr1/src",
    "PFI34": "ctr1/gate",
    "PFI33": "ctr1/aux",
    "PFI32": "ctr1/out",
    "PFI31": "ctr2/src",
    "PFI30": "ctr2/gate",
    "PFI29": "ctr2/aux",
    "PFI28": "ctr2/out",
    "PFI27": "ctr3/src",
    "PFI26": "ctr3/gate",
    "PFI25": "ctr3/aux",
    "PFI24": "ctr3/out",
    "PFI23": "ctr4/src",
    "PFI22": "ctr4/gate",
    "PFI21": "ctr4/aux",
    "PFI20": "ctr4/out",
    "PFI19": "ctr5/src",
    "PFI18": "ctr5/gate",
    "PFI17": "ctr5/aux",
    "PFI16": "ctr5/out",
    "PFI15": "ctr6/src",
    "PFI14": "ctr6/gate",
    "PFI13": "ctr6/aux",
    "PFI12": "ctr6/out",
    "PFI11": "ctr7/src",
    "PFI10": "ctr7/gate",
    "PFI9": "ctr7/aux",
    "PFI8": "ctr7/out",
}


def get_pfi(input):
    if 'pfi' in input.lower() or 'rtsi' in input.lower():
        return input
    try:
        _, card, counter, terminal = input.split('/')
    except Exception:
        raise ValueError('Wrong definition. E.g.: /Dev1/ctr0/gate')

    pfi = NI6602_PFI[counter][terminal]
    return f'/{card}/{pfi}'


def get_human(input):
    if 'rtsi' in input.lower():
        return input

    try:
        _, card, pfi = input.split('/')
    except Exception:
        raise ValueError('Wrong definition. E.g.: /Dev1/PFI39')

    human = NI6602_HUMAN[pfi]
    return f'/{card}/{human}'


def get_encoder_type(input):
    input = input.upper()
    if input == "TWO_PULSE_COUNTING":
       return EncoderType.TWO_PULSE_COUNTING
    elif input == "X_1":
        return EncoderType.X_1
    elif input == "X_2":
        return EncoderType.X_2
    elif input == "X_4":
        return EncoderType.X_4
    else:
        raise ValueError("The options are: "
                         "TWO_PULSE_COUNTING | X_1 | X_2 | X_4 ")


def get_encoder_z_index(input):
    input = input.upper()
    if input == "AHIGH_BHIGH":
        return EncoderZIndexPhase.AHIGH_BHIGH
    elif input == "AHIGH_BLOW":
        return EncoderZIndexPhase.AHIGH_BLOW
    elif input == "ALOW_BHIGH":
        return EncoderZIndexPhase.ALOW_BHIGH
    elif input == "ALOW_BLOW":
        return EncoderZIndexPhase.ALOW_BLOW
    else:
        raise ValueError("The options are: AHIGH_BHIGH | "
                         "AHIGH_BLOW | ALOW_BHIGH | ALOW_BLOW ")


def get_encoder_angle_units(input):
    input = input.upper()

    if input == "DEGREES":
        return AngleUnits.DEGREES
    elif input == "FROM_CUSTOM_SCALE":
        return AngleUnits.FROM_CUSTOM_SCALE
    elif input == "RADIANS":
        return AngleUnits.RADIANS
    elif input == "TICKS":
        return AngleUnits.TICKS
    else:
        raise ValueError("The options are: DEGREES | "
                         "FROM_CUSTOM_SCALE | RADIANS | TICKS ")

