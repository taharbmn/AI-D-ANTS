# -*- coding: utf-8 -*-

from typing import Optional, Union, List, Dict, Any

class PythonSandbox:
	"""
	A class to handle Python scripts in a sandbox environment.
	"""
	def __init__(self, content: str, filename: Optional[str] = None):
		self._content          = content
		self._start_separators = ["start", "script", "number"]
		self._end_separators   = ["end", "script", "number"]
		if not self._content:
			self._content = open(filename).read()
		self._contents = []
		marker = "```"
		if (marker in self._content.lower()):
			content = self._content
			while (marker in content.lower()):
				i = content.lower().index(marker)
				before   = str(content[:i]).strip()
				langname = content[i:]
				for c in "\r\t\n\v\f ":
					langname = langname.split(c)[0]
				after   = content[i + len(langname):].split(marker)[0]
				content = content[i + len(langname) + len(after):]
				before  = str(before).strip()
				after   = str(after).strip()
				if before:
					self._contents.append(before)
				if after:
					self._contents.append(after)
		else:
			self._contents = [ self._content ]


	def is_marker(self, line: str, markers: List[str]) -> bool:
		"""
		Check if the line contains all the markers.
		"""
		for marker in markers:
			if not (marker.lower().strip() in line.lower()):
				return False
		return True

	def is_startof_script(self, line: str) -> bool:
		"""
		Check if the line indicates the start of a script.
		"""
		return self.is_marker(line, self._start_separators)
	
	def is_endof_script(self, line: str) -> bool:
		"""
		Check if the line indicates the end of a script.
		"""
		return self.is_marker(line, self._end_separators)
	
	def is_empty_script(self, section: str) -> bool:
		"""
		Check if the script section is empty.
		"""
		_section = ""
		for line in section.split("\n"):
			line = line.strip()
			if not line or line.startswith("#"):
				continue
			_section += line + "\n"
		_section = _section.strip()
		if not _section:
			return True
		return False

	def split(self) -> List[str]:
		"""
		Split the content into scripts based on start and end markers.
		"""
		scripts = {}
		for content in self._contents:
			sections = []
			for sline in content.split("\n"):
				if not self.is_startof_script(sline):
					continue
				nosection = True
				for eline in content[content.index(sline) + len(sline):].split("\n"):
					if self.is_startof_script(eline) or self.is_endof_script(eline):
						section = content[content.index(sline) : content.index(eline) + len(eline)]
						if not self.is_empty_script(section):
							sections.append(section)
							nosection = False
						break
				if nosection:
					section = content[content.index(sline):]
					if not self.is_empty_script(section):
						sections.append(section)
			if not sections:
				sections = [content]
			for k in range(len(sections)):
				excluded = list(sections[:k] + sections[k + 1:])
				script   = str(content)
				for excluded_script in excluded:
					script = script.replace(excluded_script, "")
				scripts[str(script).strip()] = 1
		return (list(scripts))

if __name__ == "__main__":
	box = PythonSandbox(
		content  = None,
		filename = ""
	)
	print (box.split()[2])