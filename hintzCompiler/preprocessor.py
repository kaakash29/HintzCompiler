import os
import re

class Preprocessor:
    def __init__(self, include_paths=None):
        self.macros = {}
        self.include_paths = include_paths if include_paths else []

    def preprocess(self, filepath):
        return self._process_file(filepath, set())

    def _process_file(self, filepath, visited):
        if filepath in visited:
            return ""  # Prevent circular includes
        visited.add(filepath)

        output = []
        with open(filepath, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.rstrip()
            line = line.rstrip()
            stripped = line.lstrip()

            if stripped.startswith('#include'):
                match = re.match(r'#include\s+"([^"]+)"', stripped)
                if match:
                    include_file = match.group(1)
                    full_path = self._find_include_file(include_file)
                    if full_path:
                        output.append(self._process_file(full_path, visited))
                    else:
                        raise FileNotFoundError(f"Include file not found: {include_file}")
                continue

            elif line.startswith('#define'):
                parts = line.split(maxsplit=2)
                if len(parts) == 3:
                    _, key, val = parts
                    self.macros[key] = val
                continue

            for key, val in self.macros.items():
                line = re.sub(rf'\b{re.escape(key)}\b', val, line)

            output.append(line)

        return "\n".join(output)

    def _find_include_file(self, filename):
        for path in self.include_paths + ['.']:
            candidate = os.path.join(path, filename)
            if os.path.isfile(candidate):
                return candidate
        return None
