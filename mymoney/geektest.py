import sys
import unittest
import subprocess
from pathlib import Path
import re

# import geektrust

OUTPUT_NAME = "USER-OUTPUT"
OUTPUT = "OUTPUT"
INPUT = "INPUT"


def read_geektrust_input(text):
    subprocess.call(["python", "geektrust.py", text])


def split_file_w_whitespace(path):
    with open(path, "r") as fp:
        lines = [line.strip() for line in fp.readlines()]
    return [re.split(r"\s", line) for line in lines]


class GeekTest:
    def __init__(self, inputfile, outputfile):
        self.inputfile = inputfile
        self.inputpath = Path(self.inputfile)
        self.outputpath = Path(outputfile)
        self.userpath = self.get_userpath(INPUT, OUTPUT_NAME)

        self.write_output_sample()

    def get_userpath(self, text_2_replace, replacement):
        parent = self.inputpath.parent
        return parent / self.inputpath.name.replace(text_2_replace, replacement)

    def read_input_sample(self):
        with open(self.inputpath, "r") as fp:
            return [line.strip() for line in fp.readlines()]

    def write_output_sample(self):
        with open(self.userpath, "w") as f:
            subprocess.call(["python", "geektrust.py", str(self.inputfile)], stdout=f)


class TestInputOutput(unittest.TestCase):
    def test_sample_input_1(self):
        sample, output = "SAMPLE-INPUT-1.txt", "SAMPLE-OUTPUT-1.txt"
        geek1 = GeekTest(sample, output)
        wanted = split_file_w_whitespace(output)
        obtained = split_file_w_whitespace(geek1.userpath)
        self.assertListEqual(obtained, wanted)

    def test_sample_input_2(self):
        sample, output = "SAMPLE-INPUT-2.txt", "SAMPLE-OUTPUT-2.txt"
        geek2 = GeekTest(sample, output)
        wanted = split_file_w_whitespace(output)
        obtained = split_file_w_whitespace(geek2.userpath)
        self.assertListEqual(obtained, wanted)


if __name__ == "__main__":
    # GeekTest("SAMPLE-INPUT-1.txt", "SAMPLE-OUTPUT-1.txt")
    unittest.main()
    # assertListEqual(
    #     list(io.open(self.userpath)), list(io.open(self.outputpath))
    # )
    # read_geektrust_input("hello")
    testfile = Path("SAMPLE-INPUT-1.txt")
    # print(testfile.is_file())
    # write_output_sample(testfile)
