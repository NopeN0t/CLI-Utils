from typing import Union, Dict
from dataclasses import dataclass, field

OptionValue = Union[str, int, float, bool, None]

@dataclass
class Preset :
    codec : str
    base_params : Dict[str, OptionValue] = field(default_factory=dict)
    encoder_params : Dict[str, OptionValue] = field(default_factory=dict)
    rate_controls : Dict[str, OptionValue] = field(default_factory=dict)
    filters : Dict[str, OptionValue] = field(default_factory=dict)
    custom_params : str = ""
