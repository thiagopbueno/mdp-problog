# This file is part of MDP-ProbLog.

# MDP-ProbLog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MDP-ProbLog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MDP-ProbLog.  If not, see <http://www.gnu.org/licenses/>.

from problog.program import PrologString
from problog.engine  import DefaultEngine
from problog.logic   import Term

class Engine(object):
	"""
	Adapter class to Problog grounding engine.

	:param program: a valid MDP-ProbLog program
	:type program: str
	"""

	def __init__(self, program):
		self._engine = DefaultEngine()
		self._db = self._engine.prepare(PrologString(program))

	def declarations(self, declaration_type):
		"""
		Return a list of all terms of type `declaration_type`.

		:param declaration_type: declaration type.
		:type declaration_type: str
		:rtype: list of problog.logic.Term
		"""
		return [t[0] for t in self._engine.query(self._db, Term(declaration_type, None))]

	def assignments(self, assignment_type):
		"""
		Return a dictionary of assignments of type `assignment_type`.

		:param assignment_type: assignment type.
		:type assignment_type: str
		:rtype dict of (problog.logic.Term, problog.logic.Constant) items.
		"""
		return dict(self._engine.query(self._db, Term(assignment_type, None, None)))
