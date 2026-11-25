# Copyright 2026 CLR Technologies Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
"""Every source file starts with the Apache-2.0 license notice that heads this file."""

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The notice is this file's own header: every comment line before the docstring.
NOTICE = Path(__file__).read_text(encoding="utf-8").split('"""', 1)[0].rstrip("\n").split("\n")[1:]
COPYRIGHT = re.compile(r"# Copyright \d{4}(?:-\d{4})? CLR Technologies Inc\.\Z")
SUFFIXES = {".py", ".yml", ".yaml", ".sh", ".toml"}


def has_notice(text):
    lines = text.split("\n")
    if lines and lines[0].startswith("#!"):
        lines = lines[1:]
    head = lines[: len(NOTICE) + 1]
    return bool(head) and COPYRIGHT.match(head[0]) is not None and head[1:] == NOTICE


class LicenseNoticeTest(unittest.TestCase):
    def test_every_source_file_has_the_notice(self):
        files = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        missing = [
            name
            for name in files
            if (ROOT / name).suffix in SUFFIXES
            and (ROOT / name).is_file()
            and not has_notice((ROOT / name).read_text(encoding="utf-8"))
        ]
        self.assertEqual(missing, [], "files missing the Apache-2.0 notice (copy it from this file)")

    def test_a_short_header_is_rejected(self):
        self.assertFalse(has_notice("# SPDX-License-Identifier: Apache-2.0\nimport os\n"))


if __name__ == "__main__":
    unittest.main()
