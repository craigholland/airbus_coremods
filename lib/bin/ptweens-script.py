#!c:\python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'pyramid==1.5.1','console_scripts','ptweens'
__requires__ = 'pyramid==1.5.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('pyramid==1.5.1', 'console_scripts', 'ptweens')()
    )
