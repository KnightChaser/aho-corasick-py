# aho-corasick.py
from collections import deque
from typing import List, Dict, Tuple
import string


class AhoCorasick:
    def __init__(self, patterns: List[str]) -> None:
        self.patterns: List[str] = patterns
        self.trie: List[Dict[str, int]] = [{}]  # List of dicts, each is a node's children
        self.fail: List[int] = [0]  # Failure link for each node
        self.output: List[List[int]]
        self.build_trie()
        self.build_fail_links()

    def build_trie(self) -> None:
        """
        Build the trie from the list of patterns.
        Each node in the trie is represented as a dictionary mapping characters to child node indices.
        """
        self.output = [[] for _ in self.trie]  # Initialize output lists matching trie size

        for pattern_index, pattern in enumerate(self.patterns):
            node: int = 0  # start at root
            for character in pattern:
                if character not in self.trie[node]:
                    # Create a new node
                    self.trie[node][character] = len(self.trie)
                    self.trie.append({})
                    self.fail.append(0)
                    self.output.append([])
                node: int = self.trie[node][character]
            self.output[node].append(pattern_index)  # Mark the end of a pattern

    def build_fail_links(self) -> None:
        """
        Build the failure links using BFS.
        """
        queue: deque[int] = deque()

        # First, direct children to root fails to root
        for character, child in self.trie[0].items():
            self.fail[child] = 0
            queue.append(child)

        # Enqueue root's missing kids to root itself, for completeness
        alphabet: str = string.printable
        for character in alphabet:
            if character not in self.trie[0]:
                self.trie[0][character] = 0

        # BFS to build fail links
        while queue:
            current: int = queue.popleft()
            for character, child in list(self.trie[current].items()):
                queue.append(child)

                # Find the fail state for the child node
                fail_state = self.fail[current]
                while fail_state != 0 and character not in self.trie[fail_state]:
                    fail_state = self.fail[fail_state]
                fail_state = self.trie[fail_state].get(character, 0)
                self.fail[child] = fail_state

                # Chain outputs: inherit from failure node
                self.output[child].extend(self.output[fail_state])

    def search(self, text: str) -> List[Tuple[int, int]]:
        """
        Search the text for all patterns and return a list of matches.
        Each match is represented as a tuple (start_index, pattern_index).

        :param text: The text to search within.
        :return: A list of tuples indicating the start index and pattern index of each match.
        """
        matches: List[Tuple[int, int]] = []
        node: int = 0  # start at root node

        for position, character in enumerate(text):
            # Follow failures until match or root
            while node != 0 and character not in self.trie[node]:
                node = self.fail[node]
            node = self.trie[node].get(character, 0)  # Move to the next node or root(index 0)

            # Collect all outputs at this state (includes chained)
            for pattern_index in self.output[node]:
                start: int = position - len(self.patterns[pattern_index]) + 1  # Calculate start index
                matches.append((start, pattern_index))
        return matches


if __name__ == "__main__":
    patterns: List[str] = ["he", "she", "his", "hers"]
    ac: AhoCorasick = AhoCorasick(patterns)
    text: str = "ushers"
    results: List[Tuple[int, int]] = ac.search(text)

    print(f"Matches found in text '{text}':")
    for start_index, pattern_index in results:
        print(f"Pattern '{patterns[pattern_index]}' found at index {start_index}")
