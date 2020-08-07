import logging

logger = logging.getLogger(__name__)

def init_with_key_filter(class_type: type, dict_obj: dict = None, merge_unrecognised_keys: bool = True, **kwargs):

    if '__dataclass_fields__' not in class_type.__dict__:
        logger.error(f'{class_type} not a dataclass')
        return

    if dict_obj is None:
        dict_obj = dict()

    filtered_dict = dict()
    unrecognised_keys = dict()
    for i, j in {**dict_obj, **kwargs}.items():
        if i in class_type.__dict__['__dataclass_fields__'].keys():
            filtered_dict[i] = j
        else:
            unrecognised_keys[i] = j
            logger.warning(f'unrecognised key found for {class_type}: {i} {type(j)}')

    obj = class_type(**filtered_dict)

    if merge_unrecognised_keys:
        for i, j in unrecognised_keys.items():
            setattr(obj, i, j)

    return obj