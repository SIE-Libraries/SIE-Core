from typing import Dict, List, Set, Tuple, Any, Optional, Union

class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, i: int) -> int:
        if i not in self.parent:
            self.parent[i] = i
            return i
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: int, j: int) -> int:
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j
            return root_j
        return root_i

class ENode:
    def __init__(self, key: Any, children: Tuple[int, ...]):
        self.key = key
        self.children = children

    def __eq__(self, other):
        return isinstance(other, ENode) and self.key == other.key and self.children == other.children

    def __hash__(self):
        return hash((self.key, self.children))

    def __repr__(self):
        return f"{self.key}({', '.join(map(str, self.children))})"

class EClass:
    def __init__(self, eid: int):
        self.id = eid
        self.nodes: Set[ENode] = set()
        self.parents: List[Tuple[ENode, int]] = [] # (node, class_id)

    def __repr__(self):
        return f"EClass({self.id}, nodes={self.nodes})"

class EGraph:
    def __init__(self):
        self.union_find = UnionFind()
        self.classes: Dict[int, EClass] = {}
        self.memo: Dict[ENode, int] = {}
        self.next_id = 0
        self.worklist: Set[int] = set()

    def find(self, eid: int) -> int:
        return self.union_find.find(eid)

    def add(self, enode: ENode) -> int:
        enode = ENode(enode.key, tuple(self.find(c) for c in enode.children))
        if enode in self.memo:
            return self.find(self.memo[enode])

        new_id = self.next_id
        self.next_id += 1
        self.union_find.parent[new_id] = new_id

        eclass = EClass(new_id)
        eclass.nodes.add(enode)
        self.classes[new_id] = eclass
        self.memo[enode] = new_id

        for child_id in enode.children:
            self.classes[self.find(child_id)].parents.append((enode, new_id))
        return new_id

    def union(self, id1: int, id2: int) -> int:
        id1 = self.find(id1)
        id2 = self.find(id2)
        if id1 == id2:
            return id1

        new_id = self.union_find.union(id1, id2)
        self.worklist.add(id1)
        self.worklist.add(id2)
        return new_id

    def rebuild(self):
        if self.worklist:
            self.worklist = set()
            self._full_rebuild()

    def _full_rebuild(self):
        changed = True
        while changed:
            changed = False
            new_memo = {}
            new_classes = {}

            # Map of canonical nodes to their representative class ID
            node_to_id = {}

            for eid in list(self.classes.keys()):
                root = self.find(eid)
                if root not in new_classes:
                    new_classes[root] = EClass(root)

                eclass = self.classes[eid]
                for node in eclass.nodes:
                    canon_node = ENode(node.key, tuple(self.find(c) for c in node.children))
                    if canon_node in node_to_id:
                        other_root = self.find(node_to_id[canon_node])
                        if other_root != root:
                            new_root = self.union_find.union(other_root, root)
                            root = new_root
                            changed = True
                    node_to_id[canon_node] = root
                    if root not in new_classes:
                        new_classes[root] = EClass(root)
                    new_classes[root].nodes.add(canon_node)

            # Update classes to only include representatives
            self.classes = {eid: cls for eid, cls in new_classes.items() if self.find(eid) == eid}
            self.memo = node_to_id
            if not changed:
                break

        # After rebuild, update parents
        for eclass in self.classes.values():
            eclass.parents = []
        for eid, eclass in self.classes.items():
            for node in eclass.nodes:
                for child_id in node.children:
                    child_root = self.find(child_id)
                    if child_root in self.classes:
                        self.classes[child_root].parents.append((node, eid))

class Pattern:
    def __init__(self, content: Union[str, Tuple[str, Tuple['Pattern', ...]]]):
        self.content = content

    def __repr__(self):
        return str(self.content)

    def match(self, egraph: EGraph) -> List[Tuple[int, Dict[str, int]]]:
        matches = []
        for eid in egraph.classes:
            for subst in self._match_class(egraph, eid):
                matches.append((eid, subst))
        return matches

    def _match_class(self, egraph: EGraph, eid: int) -> List[Dict[str, int]]:
        eid = egraph.find(eid)
        results = []
        if isinstance(self.content, str):
            # It's a variable or a constant without children
            # If it starts with '?', it's a variable
            if self.content.startswith('?'):
                results.append({self.content: eid})
            else:
                # It's a leaf node key
                for node in egraph.classes[eid].nodes:
                    if node.key == self.content and not node.children:
                        results.append({})
        else:
            key, children = self.content
            for node in egraph.classes[eid].nodes:
                if node.key == key and len(node.children) == len(children):
                    # Try to match children
                    child_matches = [{}]
                    for i in range(len(children)):
                        new_child_matches = []
                        sub_matches = children[i]._match_class(egraph, node.children[i])
                        for m1 in child_matches:
                            for m2 in sub_matches:
                                # Merge substitutions, checking for consistency
                                merged = dict(m1)
                                consistent = True
                                for var, val in m2.items():
                                    if var in merged and merged[var] != val:
                                        consistent = False
                                        break
                                    merged[var] = val
                                if consistent:
                                    new_child_matches.append(merged)
                        child_matches = new_child_matches
                    results.extend(child_matches)
        return results

    def apply(self, egraph: EGraph, subst: Dict[str, int]) -> int:
        if isinstance(self.content, str):
            if self.content.startswith('?'):
                return subst[self.content]
            else:
                return egraph.add(ENode(self.content, ()))
        else:
            key, children = self.content
            child_ids = tuple(child.apply(egraph, subst) for child in children)
            return egraph.add(ENode(key, child_ids))

class Rewrite:
    def __init__(self, name: str, lhs: Pattern, rhs: Pattern):
        self.name = name
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return f"Rewrite({self.name}: {self.lhs} -> {self.rhs})"

    def run(self, egraph: EGraph) -> List[Tuple[int, int]]:
        matches = self.lhs.match(egraph)
        unions = []
        for eid, subst in matches:
            rhs_id = self.rhs.apply(egraph, subst)
            if egraph.find(eid) != egraph.find(rhs_id):
                unions.append((eid, rhs_id))
        return unions

class Runner:
    def __init__(self, egraph: EGraph, iter_limit: int = 10, node_limit: int = 1000):
        self.egraph = egraph
        self.iter_limit = iter_limit
        self.node_limit = node_limit
        self.iterations = 0

    def run(self, rewrites: List[Rewrite]):
        for _ in range(self.iter_limit):
            self.iterations += 1
            all_unions = []
            for rewrite in rewrites:
                all_unions.extend(rewrite.run(self.egraph))

            if not all_unions:
                break

            for id1, id2 in all_unions:
                self.egraph.union(id1, id2)

            self.egraph.rebuild()

            if len(self.egraph.memo) > self.node_limit:
                break
