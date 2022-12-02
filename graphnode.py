import sys

class GraphNode:
    ROOT_DEFAULT_NAME = '<[root]>'

    @classmethod
    def create_root(cls, content):
        return cls(content or cls.ROOT_DEFAULT_NAME, parent=None, branch_id=0, known_contents=set())

    def __init__(self, content, parent, branch_id=None, known_contents=None):
        self.content = content
        self.parent = parent
        self.children = []
        self._branch_id = branch_id
        self._last_branch_id = branch_id
        self._known_contents = known_contents

    def add_or_insert(self, content):
        found = self.find_child(content)
        if found:
            #print("Found %s in tree already" % (content))
            return found
        else:
            return self.add_child(content)
            
    def find_child(self, content):
        for child in self.children:
            if child.content==content:
                return child
        return None
        
    def add_child(self, content):
        while content and content in self.known_contents:
            print("Adding child %s of parent %s" % (content, self.content))
            print('ERROR: Duplicate content found: {}. Using workaround'.format(content), file=sys.stderr)
            content = content + ' '
        self.known_contents.add(content)
        branch_id = None if self.parent else self.incr_last_branch_id()
        child = self.__class__(content, parent=self, branch_id=branch_id)
        self.children.append(child)
        return child

    def set_single_child_as_root(self):
        assert not self.parent, 'This should only be called on a graph root'
        if self.content != self.ROOT_DEFAULT_NAME or len(self.children) != 1:
            return self
        old_root = self
        new_root = old_root.children[0]
        new_root._known_contents = old_root._known_contents
        new_root.parent = None
        new_root._reset_branch_ids()
        return new_root

    def _reset_branch_ids(self):
        assert not self.parent, 'This should only be called on a graph root'
        self._branch_id = 0
        self._last_branch_id = 0
        for child in self.children:
            child._branch_id = self.incr_last_branch_id()

    @property
    def branch_id(self):
        node = self
        while node._branch_id is None and node.parent:
            node = node.parent
        return node._branch_id

    @property
    def known_contents(self):
        node = self
        while node._known_contents is None and node.parent:
            node = node.parent
        return node._known_contents

    @property
    def depth(self):
        depth = 0
        node = self
        while node.parent:
            node = node.parent
            depth += 1
        return depth

    @property
    def height(self):
        if not self.children:
            return 1
        return 1 + max(child.height for child in self.children)

    def incr_last_branch_id(self):
        node = self
        while node._last_branch_id is None and node.parent:
            node = node.parent
        node._last_branch_id += 1
        return node._last_branch_id

    def __str__(self, indent=''):
        should_indent = self.content and self.content != self.ROOT_DEFAULT_NAME
        out = indent + self.content + '\n' if should_indent else ''
        if should_indent:
            indent += '    '
        for child in self.children:
            out += child.__str__(indent)
        return out

    def __iter__(self):
        yield self
        for child in self.children:
            yield from child