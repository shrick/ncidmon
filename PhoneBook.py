#!/usr/bin/env python
# -*- coding: utf8 -*-

# system
import string

# application
import misc

phonebook = {}


def resolve_number(number):
    return phonebook.get(str(number))

def _get_normalized_phonebook(directory):
    # create identity table
    all = string.maketrans('','')
    
    # make translation table w/o digits
    no_digits = all.translate(all, string.digits)
    
    # return re-built directory with normalized numbers
    return {
        key.translate(None, no_digits): value
            for (key, value) in directory.items()
    }


# import mapping of numbers to names
try:
    import subscribers
    # # Python file with simple dictionary
    # # -*- coding: utf8 -*-
    #
    # directory = {
    #     '0123 / 45 67 - 89': 'John Doo',
    #     '0132435465': 'Mary Jane'
    # }
    
    # store normalized telephone numbers of numbers found in adressbook
    phonebook.update(_get_normalized_phonebook(subscribers.directory))
    misc.dprint('phonebook found')
except:
    misc.dprint('no phonebook found')

