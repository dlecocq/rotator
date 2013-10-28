'''Tests for the rotator'''

import os
import Queue
import rotator
import unittest
import threading


class Pipe(object):
    def __init__(self):
        self.queue = Queue.Queue()

    def readline(self):
        '''Read a line'''
        return self.queue.get()

    def writeline(self, line):
        '''Write a line'''
        self.queue.put(line)

    def __iter__(self):
        line = self.readline()
        while line:
            yield line
            line = self.readline()

    def __enter__(self):
        return self

    def __exit__(self, typ, val, trace):
        self.writeline('')
        if typ:
            raise typ, val, trace


class TestBase(unittest.TestCase):
    def setUp(self):
        # Make sure we have a tmpdir
        self.tmpdir = 'tmp'
        if not os.path.exists(self.tmpdir):
            os.mkdir(self.tmpdir)
        self.fin = Pipe()

    def tearDown(self):
        # Remove everything from the tmpdir
        for path in os.listdir(self.tmpdir):
            os.remove(self.tmp(path))

    def tmp(self, name):
        '''Path to the temp file'''
        return os.path.join(self.tmpdir, name)


class TestWatched(TestBase):
    def test_buffered(self):
        '''Get some coverage for buffered line reading'''
        log = rotator.Watched(self.tmp('foo.out'), fin=self.fin)
        expected = ['hello'] * 1000
        with self.fin:
            for line in expected:
                self.fin.writeline(line)
        self.assertEqual(expected, list(log.lines(True)))

    def test_basic(self):
        '''We should be able to use a basic watched file'''
        with self.fin:
            path = self.tmp('foo.out')
            thread = threading.Thread(
                target=rotator.Watched(path, fin=self.fin).run)
            thread.start()
            self.fin.writeline('hello')
            os.rename(path, self.tmp('bar.out'))
            self.fin.writeline('howdy')
        thread.join()
        # The watcher should have reopened the file
        self.assertTrue(os.path.exists(path))


class TestSignaled(TestBase):
    def test_basic(self):
        '''We should be able to use a signaled handler'''
        path = self.tmp('foo.out')
        log = rotator.Signaled(path, fin=self.fin, sig='USR1')
        os.rename(path, self.tmp('bar.out'))
        log.handle(None, None)
        # The logger should have reopened the file
        self.assertTrue(os.path.exists(path))

    def test_missing_signal(self):
        '''Raises an error if we don't have that particular signal'''
        self.assertRaises(
            ValueError, rotator.Signaled, self.tmp('foo.out'), sig='JSLFJKSFJ')


class TestRotated(TestBase):
    def test_parse_size(self):
        '''We should be able to parse human-readable sizes'''
        examples = [
            ('1024'   , 1024),
            ('1024 kB', 1024 * 1024),
            (' 1 MB  ', 1024 * 1024),
            (' 1 gb  ', 1024 * 1024 * 1024)
        ]
        for string, size in examples:
            self.assertEqual(rotator.Rotated.parse_size(string), size)

    def test_invalid_sizes(self):
        '''Raises errors for invalid size'''
        examples = [
            '',
            '0s98f',
            '10294 TB'
        ]
        for string in examples:
            print string
            self.assertRaises(ValueError, rotator.Rotated.parse_size, string)
