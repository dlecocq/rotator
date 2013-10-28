'''Our rotator classes'''

import re
import sys
import signal
import logging
import logging.handlers


class Rotator(object):
    '''Base class for all rotators'''
    def __init__(self, handler, fin=sys.stdin):
        self.fin = fin
        # Set up the level and formatter
        self.handler = handler
        self.handler.setFormatter(logging.Formatter('%(message)s'))
        self.handler.setLevel(logging.DEBUG)

        # Attach it to the logger
        self.logger = logging.getLogger('rotator')
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def reopen(self, handler):
        '''Replace our existing handler with this new one'''
        # This /could/ result in duplicate records, though it's unlikely. It's
        # also preferred to missing records
        self.logger.addHandler(handler)
        self.logger.removeHandler(self.handler)
        self.handler = handler

    def lines(self, buffered=False):
        '''Generator for all the lines from stdin'''
        while True:
            try:
                if buffered:
                    for line in self.fin:
                        yield line.strip('\n')
                    # When we're done yielding lines, break
                    break
                else:
                    line = self.fin.readline()
                    while line:
                        yield line.strip('\n')
                        line = self.fin.readline()
                    # When we're done reading lines, break
                    break
            except IOError as exc:  # pragma: no cover
                print 'Warning: %s' % exc

    def run(self, buffered=False):
        '''Repeat lines from stdin to the logger'''
        for line in self.lines(buffered):
            self.logger.debug(line)


class Watched(Rotator):
    '''Watched file handler'''
    def __init__(self, path, mode='a', fin=sys.stdin):
        Rotator.__init__(
            self, logging.handlers.WatchedFileHandler(path, mode), fin)


class Signaled(Rotator):
    '''Signaled handler'''
    def __init__(self, path, mode='a', sig='HUP', fin=sys.stdin):
        if not hasattr(signal, 'SIG' + sig):
            raise ValueError, 'No such signal SIG%s' % sig
        self.signal = getattr(signal, 'SIG' + sig)
        self.path = path
        Rotator.__init__(self, logging.FileHandler(path, mode))

    def handle(self, signum, frame):
        '''Rotate our file'''
        self.reopen(logging.FileHandler(self.path))

    def run(self, *args, **kwargs):
        '''Repeat lines from stdin to the logger'''
        signal.signal(self.signal, self.handle)
        Rotator.run(self, *args, **kwargs)


class Rotated(Rotator):
    '''Self-rotating handler'''
    def __init__(self, path, mode='a', size=None, count=None, fin=sys.stdin):
        size = self.parse_size(str(size or 0))
        count = count or 5
        Rotator.__init__(self,
            logging.handlers.RotatingFileHandler(path, mode, size, count), fin)

    @classmethod
    def parse_size(cls, size):
        '''Return a size in bytes'''
        regex = r'\s*(\d+)\s*([kKmMgG][bB])?\s*$'
        match = re.match(regex, size)
        if not match:
            raise ValueError, '%s does not match %s' % (regex, size)
        size = int(match.group(1))
        units = match.group(2)
        if not units:
            return size
        if units.lower() == 'kb':
            return size * 1024
        elif units.lower() == 'mb':
            return size *  1024 * 1024
        elif units.lower() == 'gb':
            return size * 1024 * 1024 * 1024
