""" This module provides support for dumping all EIONET styles from Zope
    to an external folder.

    How to use it from ZOPE's ZMI:

        0. Go to the style main folder - /styles_source

        1. Create an External Method:
            Id:             dump_styles
            Module name:    eionet_external.dump_styles
            Function name:  dump_styles

        2. Create a Script (Python):
            Id:     dump_styles.py
            Body:   return context.dump_styles(context, '/opt/zope/var')

        3. Execute the python script:
            - click on the object dump_styles.py
            - click/follow the Test tab
"""

import logging
from os.path import join, isdir
from os import mkdir

logger = logging.getLogger('eionet_external')

STYLES_FOLDER_NAME = 'styles'

STYLES_TREE = [
    'eionet2007',
    'eionet2016',
    'handheld',
    'FlowPlayerThermo.swf',
    'logo60x60.png',
    'sortdown.gif',
    'sortnot.gif',
    'sortup.gif'
]

STYLES_META_TYPES = [
    'Folder',
    'File',
    'Image',
    'DTML Method'
]

class DumpStyles:

    def __init__(self, context, dump_path):
        self.context = context
        self.dump_path = dump_path

    def __create_folder(self, path):
        if not isdir(path):
            try:
                mkdir(path)
            except:
                raise OSError, 'Can\'t create directory {}'.format(
                    path
                )

    def __create_file(self, path, data):
        f = open(path, 'wb')
        f.write(data)
        f.close()

    def __dump_item(self, ob, path, level):
        logger.info('{} dumping {}'.format('-'*level, ob.absolute_url(1)))
        ob_path = join(path, ob.getId())
        if ob.meta_type == 'Folder':
            #create directory if missing
            self.__create_folder(ob_path)
            #handle subobjects
            for item in ob.objectValues(STYLES_META_TYPES):
                self.__dump_item(item, ob_path, level*2)
        elif ob.meta_type in ['File', 'Image']:
            data = str(ob.data)
            self.__create_file(ob_path, data)
        elif ob.meta_type == 'DTML Method':
            data = ob(
                ob.getParentNode(),
                REQUEST=self.context.REQUEST,
                RESPONSE=self.context.REQUEST.RESPONSE)
            self.__create_file(ob_path, data)

    def trigger(self):
        """ Parses styles tree and export all its contents.
        """
        styles_path = join(
            self.dump_path,
            STYLES_FOLDER_NAME
        )
        self.__create_folder(styles_path)
        logger.info('START dumping styles @ {} to {}'.format(
            self.context.absolute_url(1),
            styles_path)
        )
        for item_id in STYLES_TREE:
            item = self.context._getOb(item_id, None)
            if item is not None:
                self.__dump_item(
                    item,
                    styles_path,
                    1
                )
        logger.info('FINISHED dumping styles')
        return 'FINISHED dumping styles @ {} to {}'.format(
            self.context.absolute_url(1),
            styles_path
        )

def dump_styles(context, dump_path):
    """ Entry point that must used as 'Function Name'
    """
    dumper = DumpStyles(context, dump_path)
    return dumper.trigger()
