# -*- coding: utf-8 -*-

import os
from importlib import resources

def install() :
    support_path = resources.files('psox').joinpath('support')
    os.system(str(support_path / 'embed_sox.cmd'))
