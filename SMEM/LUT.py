from ExactMatch import ExactMatch
import json
from os import path


class LUT:

    def __init__(self, matcher: ExactMatch):
        self.matcher = matcher
        if self.matcher.ref_sequence is None:
            self.matcher.load_ref_sequence()
        self.lut = None
        self.lut_size = None

    def generate_lut(self, size):
        self.lut_size = size
        self.lut = {}
        ref = self.matcher.ref_sequence[:self.matcher.ref_size-1]

        for pos in range(self.matcher.ref_size):

            for i in range(size):
                if self.matcher.ref_size - size > pos-i >= 0:
                    substring = ref[pos-i:pos+size-i]

                    encoded_substring = self.convert_seq_to_num(substring)

                    if encoded_substring not in self.lut:

                        # TODO -- Maybe can generate this during fm_index to directly get suffix location
                        # self.lut[substring] = self.matcher.exact_match_back_prop(substring)

                        suf_indexes = self.matcher.exact_match_back_prop(substring)
                        ref_indexes = self.matcher.get_positions(suf_indexes[0], suf_indexes[1])
                        self.lut[str(encoded_substring)] = [suf_indexes, ref_indexes]

    @staticmethod
    def convert_seq_to_num(sequence):
        nucleo = {}
        nucleo['A'] = 0
        nucleo['C'] = 1
        nucleo['G'] = 2
        nucleo['T'] = 3

        conversion = 0
        for j in range(len(sequence)):
            conversion = conversion << 2 | nucleo[sequence[j]]
        return conversion

    def save_lut(self):
        if self.lut is None:
            raise RuntimeError("LUT has not been created yet.")

        lut_file = path.join("data", self.matcher.ref_seq_file.split(".")[0] + "-LUT.json")
        with open(lut_file, "w") as lut_f:
            lut_f.write(json.dumps({"lut": self.lut, "lut_size": self.lut_size}, indent=4, sort_keys=True))

    def load_lut(self):
        lut_file = path.join("data", self.matcher.ref_seq_file.split(".")[0] + "-LUT.json")
        with open(lut_file, "r") as lut_f:
            lut_json = json.load(lut_f)
            self.lut = lut_json["lut"]
            self.lut_size = lut_json["lut_size"]


if __name__ == '__main__':
    matcher = ExactMatch("big_data.fa")
    lut = LUT(matcher)
    lut.generate_lut(3)
    lut.save_lut()
