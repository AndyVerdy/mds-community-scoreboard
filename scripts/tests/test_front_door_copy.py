"""The front door's refusal copy must never assert a fact it does not know (#125).

Three different things put a sender on the non-member path, and they are NOT the same
statement about that person:

  * no row at all                -> we cannot match this number
  * a row whose status is NULL   -> the number is not connected to a member record yet
  * a row whose status says      -> that membership really is not active
    'Removed - Canceled', etc.

Collapsing the middle case into the third is what told Shyam Murali, a paying Current
Member, that his membership "is not currently active" during the Summit launch.

These tests run the REAL `Resolve Member` and `Build Generic` code out of the live n8n
graph (or a snapshot), so they cannot drift from what is deployed.

Run:  python3 -m unittest scripts.tests.test_front_door_copy -v      (from the repo root)
      OLIVIA_WF_REF=prod python3 -m unittest scripts.tests.test_front_door_copy -v
Needs: node on PATH, and network for the default ref (staging).
"""
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import olivia_wf  # noqa: E402

REF = os.environ.get("OLIVIA_WF_REF", "staging")
ACTIVE_STATUSES = ["Current Member", "New Member", "Current Member- Not Renewing", "Staff"]

# The sentence that may only ever be said about a status field that carries an inactive
# value. If it reaches any other class, the door is lying to a member.
INACTIVE_CLAIM = "not currently active"


def _node_code(nodes, name):
    for n in nodes:
        if n["name"] == name:
            return n["parameters"]["jsCode"]
    raise AssertionError(f"node {name!r} is not in the {REF} graph")


class FrontDoor:
    """Runs the two Code nodes exactly as n8n would, with stubbed n8n globals."""

    def __init__(self):
        graph, _ = olivia_wf.load_graph(REF)
        nodes = graph["nodes"]
        self.resolve = _node_code(nodes, "Resolve Member")
        self.generic = _node_code(nodes, "Build Generic")

    @staticmethod
    def _run(js):
        out = subprocess.run(["node", "-e", js], capture_output=True, text=True)
        if out.returncode != 0:
            raise AssertionError(f"node failed: {out.stderr.strip()[:600]}")
        return json.loads(out.stdout)

    def resolve_member(self, rows, inbound=None):
        inbound = {"text": "who is around me?", "from": "919940669944", **(inbound or {})}
        js = f"""
        const __rows = {json.dumps(rows)};
        const __inbound = {json.dumps(inbound)};
        const $input = {{ all: () => __rows.map(r => ({{ json: r }})) }};
        const $ = (name) => ({{ first: () => ({{ json: name === 'Log Inbound' ? __inbound : {{}} }}) }});
        const __out = (function () {{ {self.resolve} }})();
        console.log(JSON.stringify(__out[0].json));
        """
        return self._run(js)

    def build_generic(self, resolved):
        js = f"""
        const __m = {json.dumps(resolved)};
        const $input = {{ first: () => ({{ json: __m }}) }};
        const __out = (function () {{ {self.generic} }})();
        console.log(JSON.stringify(__out[0].json));
        """
        return self._run(js)

    def reply_for(self, rows, inbound=None):
        """The full door: rows in, member-facing sentence out (or None when matched)."""
        resolved = self.resolve_member(rows, inbound)
        if resolved.get("matched"):
            return resolved, None
        return resolved, self.build_generic(resolved)["reply"]


def _row(**kw):
    base = {
        "phone": "919940669944",
        "full_name": "Test Sender",
        "name": "Test Sender",
        "membership_status": "Current Member",
        "at_member_id": "recTEST0000000001",
        "airtable_id": "recWATEST00000001",
        "channels_present": [],
        "olivia_welcomed_at": None,
        "olivia_optout_at": None,
    }
    base.update(kw)
    return base


class UnlinkedNumberIsNotAnInactiveMembership(unittest.TestCase):
    """#125 — the bug, stated as a test."""

    @classmethod
    def setUpClass(cls):
        cls.door = FrontDoor()

    def test_null_status_never_claims_the_membership_is_inactive(self):
        resolved, reply = self.door.reply_for([_row(membership_status=None)])
        self.assertFalse(resolved["matched"])
        self.assertNotIn(INACTIVE_CLAIM, reply.lower(),
                         "a row with NO status must not be told their membership is inactive")

    def test_empty_status_never_claims_the_membership_is_inactive(self):
        _, reply = self.door.reply_for([_row(membership_status="")])
        self.assertNotIn(INACTIVE_CLAIM, reply.lower())

    def test_whitespace_status_never_claims_the_membership_is_inactive(self):
        _, reply = self.door.reply_for([_row(membership_status="   ")])
        self.assertNotIn(INACTIVE_CLAIM, reply.lower())

    def test_unlinked_reason_is_its_own_class(self):
        resolved, _ = self.door.reply_for([_row(membership_status=None)])
        self.assertEqual(resolved["reason"], "unlinked")

    def test_unlinked_copy_tells_them_how_to_get_connected(self):
        _, reply = self.door.reply_for([_row(membership_status=None)])
        self.assertIn("email", reply.lower(),
                      "the unlinked message must ask for the email on their MDS account")


class TheOtherClassesAreUnchanged(unittest.TestCase):
    """Every neighbouring class keeps the behaviour it already had."""

    @classmethod
    def setUpClass(cls):
        cls.door = FrontDoor()

    def test_a_genuinely_inactive_status_still_says_so(self):
        resolved, reply = self.door.reply_for(
            [_row(membership_status="Removed - Canceled Membership")])
        self.assertEqual(resolved["reason"], "inactive")
        self.assertIn(INACTIVE_CLAIM, reply.lower())

    def test_removed_for_cause_is_inactive(self):
        resolved, _ = self.door.reply_for([_row(membership_status="Removed - For Cause")])
        self.assertEqual(resolved["reason"], "inactive")

    def test_active_statuses_all_pass_the_door(self):
        for status in ACTIVE_STATUSES:
            with self.subTest(status=status):
                resolved, _ = self.door.reply_for([_row(membership_status=status)])
                self.assertTrue(resolved["matched"], f"{status} must reach the member path")

    def test_no_row_is_no_match(self):
        resolved, reply = self.door.reply_for([])
        self.assertEqual(resolved["reason"], "no_match")
        self.assertNotIn(INACTIVE_CLAIM, reply.lower())

    def test_hidden_number_is_unknown_uid(self):
        resolved, reply = self.door.reply_for([], inbound={"from_is_uid": True})
        self.assertEqual(resolved["reason"], "unknown_uid")
        self.assertNotIn(INACTIVE_CLAIM, reply.lower())

    def test_two_rows_is_ambiguous(self):
        resolved, reply = self.door.reply_for([_row(), _row(at_member_id="recTEST0000000002")])
        self.assertEqual(resolved["reason"], "ambiguous")
        self.assertNotIn(INACTIVE_CLAIM, reply.lower())


class OnlyTheInactiveClassMayMakeTheInactiveClaim(unittest.TestCase):
    """The invariant, checked across every class at once."""

    @classmethod
    def setUpClass(cls):
        cls.door = FrontDoor()

    def test_sweep(self):
        cases = {
            "unlinked_null": ([_row(membership_status=None)], None),
            "unlinked_empty": ([_row(membership_status="")], None),
            "no_match": ([], None),
            "unknown_uid": ([], {"from_is_uid": True}),
            "ambiguous": ([_row(), _row(at_member_id="recTEST0000000002")], None),
            "inactive": ([_row(membership_status="Removed - Canceled Membership")], None),
        }
        claimed = set()
        for label, (rows, inbound) in cases.items():
            _, reply = self.door.reply_for(rows, inbound)
            if INACTIVE_CLAIM in reply.lower():
                claimed.add(label)
        self.assertEqual(claimed, {"inactive"},
                         "only the genuinely-inactive class may say a membership is not active")


if __name__ == "__main__":
    unittest.main()
