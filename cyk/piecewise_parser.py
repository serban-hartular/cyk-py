
from cyk.prob_parser import *
from cyk.grammar import *

class PiecewiseParser(ProbabilisticParser):
    def __init__(self, grammar : Grammar):
        super().__init__(grammar)
        self.span_list = []
        self.latest_nodes = []
        self.parse_complete = True
    @staticmethod
    def is_span_splitter(sq : ParseSquare):
        return len(sq) == 1 and str(sq[0].data[TYPE_STR]) == 'PUNCT'
    @staticmethod
    def span_splitter(input_sqs : List[ParseSquare]) -> List[range]:
        spans : List[range] = []
        start = 0
        for i, sq in enumerate(input_sqs):
            if PiecewiseParser.is_span_splitter(sq):
                if i > start:
                    spans.append(range(start, i))
                start = i+1
        if start < len(input_sqs):
            spans.append(range(start, len(input_sqs)))
        return spans
    def input(self, input : List[ParseSquare], exclude_similar = True):
        super().input(input, exclude_similar)
        self.span_list = PiecewiseParser.span_splitter(input)
    def parse_span(self, span : range, coord_generator = None) -> int:
        self.latest_nodes = []
        if coord_generator is None:
            coord_generator = ProbabilisticParser.word_order
        nodes_added = 0
        N = len(span)
        # for row in range(0, N):
        #     for col in range(span.start, span.stop-row):
        for row, col in coord_generator(N):
            col = col + span.start
            if self.parse_complete:
                nodes_added += Parser.do_square(self, row, col)
            else:
                nodes_added += self.do_square(row, col)
            self.latest_nodes.append((row, col))
        return nodes_added
    def next_parse(self, coord_generator = None) -> int:
        nodes_added = 0
        for span in self.span_list:
            nodes_added += self.parse_span(span, coord_generator)
        return nodes_added
    