from dexy.artifact import FilterArtifact
from dexy.artifact import InitialArtifact
from dexy.artifact import InitialVirtualArtifact
from dexy.common import OrderedDict
from dexy.doc import Doc
from dexy.tests.utils import tempdir
from dexy.tests.utils import wrap
from dexy.wrapper import Wrapper
import dexy.exceptions
import time

def test_no_data():
    with wrap() as wrapper:
        doc = Doc("hello.txt", wrapper=wrapper)
        try:
            wrapper.run_docs(doc)
            assert False, 'should raise UserFeedback'
        except dexy.exceptions.UserFeedback as e:
            assert "No contents found" in e.message

def test_caching():
    with tempdir():
        wrapper1 = Wrapper()
        wrapper1.setup_dexy_dirs()

        with open("abc.txt", "w") as f:
            f.write("these are the contents")

        doc1 = Doc("abc.txt|dexy", wrapper=wrapper1)
        wrapper1.run_docs(doc1)

        assert isinstance(doc1.artifacts[0], InitialArtifact)
        hashstring_0_1 = doc1.artifacts[0].hashstring

        assert isinstance(doc1.artifacts[1], FilterArtifact)
        hashstring_1_1 = doc1.artifacts[1].hashstring

        wrapper2 = Wrapper()
        doc2 = Doc("abc.txt|dexy", wrapper=wrapper2)
        wrapper2.run_docs(doc2)

        assert isinstance(doc2.artifacts[0], InitialArtifact)
        hashstring_0_2 = doc2.artifacts[0].hashstring

        assert isinstance(doc2.artifacts[1], FilterArtifact)
        hashstring_1_2 = doc2.artifacts[1].hashstring

        assert hashstring_0_1 == hashstring_0_2
        assert hashstring_1_1 == hashstring_1_2

def test_caching_virtual_file():
    with tempdir():
        wrapper1 = Wrapper()
        wrapper1.setup_dexy_dirs()

        doc1 = Doc("abc.txt|dexy",
                contents = "these are the contents",
                wrapper=wrapper1)
        wrapper1.run_docs(doc1)

        assert isinstance(doc1.artifacts[0], InitialVirtualArtifact)
        hashstring_0_1 = doc1.artifacts[0].hashstring

        assert isinstance(doc1.artifacts[1], FilterArtifact)
        hashstring_1_1 = doc1.artifacts[1].hashstring

        wrapper2 = Wrapper()
        doc2 = Doc(
                "abc.txt|dexy",
                contents = "these are the contents",
                wrapper=wrapper2)
        wrapper2.run_docs(doc2)

        assert isinstance(doc2.artifacts[0], InitialVirtualArtifact)
        hashstring_0_2 = doc2.artifacts[0].hashstring

        assert isinstance(doc2.artifacts[1], FilterArtifact)
        hashstring_1_2 = doc2.artifacts[1].hashstring

        assert hashstring_0_1 == hashstring_0_2
        assert hashstring_1_1 == hashstring_1_2

def test_virtual_artifact():
    with wrap() as wrapper:
        a = InitialVirtualArtifact("abc.txt",
                contents="these are the contents",
                wrapper=wrapper)

        a.name = "abc.txt"
        a.run()

        assert a.output_data.is_cached()
        assert a.output_data.data() == "these are the contents"

def test_initial_artifact_hash():
    with wrap() as wrapper:
        filename = "source.txt"

        with open(filename, "w") as f:
            f.write("hello this is some text")

        artifact = InitialArtifact(filename, wrapper=wrapper)
        artifact.name = filename
        artifact.run()

        first_hashstring = artifact.hashstring

        time.sleep(1.1) # make sure mtime is at least 1 second different

        with open(filename, "w") as f:
            f.write("hello this is different text")

        artifact = InitialArtifact(filename, wrapper=wrapper)
        artifact.name = filename
        artifact.run()

        second_hashstring = artifact.hashstring

        assert first_hashstring != second_hashstring

def test_parent_doc_hash():
    with tempdir():
        args = [["hello.txt|newdoc", { "contents" : "hello" }]]
        wrapper = Wrapper(*args)
        wrapper.setup_dexy_dirs()
        wrapper.run()

        doc = wrapper.registered_docs()[0]
        hashstring = doc.final_artifact.hashstring

        wrapper.setup_run()
        rows = wrapper.get_child_hashes_in_previous_batch(hashstring)


def test_parent_doc_hash_2():
    with tempdir():
        args = [["hello.txt|newdoc", { "contents" : "hello" }]]
        wrapper = Wrapper(*args)
        wrapper.setup_dexy_dirs()
        wrapper.run()

        for doc in wrapper.registered_docs():
            if doc.__class__.__name__ == 'FilterArtifact':
                assert doc.source == 'generated'

        wrapper = Wrapper(*args)
        wrapper.run()

        for doc in wrapper.registered_docs():
            if doc.__class__.__name__ == 'FilterArtifact':
                assert doc.source == 'cached'

def test_bad_file_extension_exception():
    with wrap() as wrapper:
        doc = Doc("hello.abc|py",
                contents="hello",
                wrapper=wrapper)

        try:
            wrapper.run_docs(doc)
            assert False, "should not be here"
        except dexy.exceptions.UserFeedback as e:
            assert "Filter 'py' in 'hello.abc|py' can't handle file extension .abc" in e.message

def test_custom_file_extension():
    with wrap() as wrapper:
        doc = Doc("hello.py|pyg",
                contents="""print "hello, world" """,
                pyg = { "ext" : ".tex" },
                wrapper=wrapper)
        wrapper.run_docs(doc)
        assert "begin{Verbatim}" in doc.output().as_text()

def test_choose_extension_from_overlap():
    with wrap() as wrapper:
        doc = Doc("hello.py|pyg|forcelatex",
                contents="""print "hello, world" """,
                wrapper=wrapper)
        wrapper.run_docs(doc)
        assert "begin{Verbatim}" in doc.output().as_text()

def test_no_file_extension_overlap():
    with wrap() as wrapper:
        doc = Doc("hello.txt|forcetext|forcehtml",
                contents="hello",
                wrapper=wrapper)

        try:
            wrapper.run_docs(doc)
            assert False, "UserFeedback should be raised"
        except dexy.exceptions.UserFeedback as e:
            assert "Filter forcehtml can't go after filter forcetext, no file extensions in common." in e.message

def test_virtual_artifact_data_class_generic():
    with wrap() as wrapper:
        doc = Doc("virtual.txt",
                contents = "virtual",
                wrapper=wrapper)
        artifact = doc.artifacts[0]
        assert artifact.__class__.__name__ == "InitialVirtualArtifact"
        assert artifact.data_class_alias() == 'generic'

def test_virtual_artifact_data_class_sectioned():
    with wrap() as wrapper:
        contents = OrderedDict()
        contents['foo'] = 'bar'
        doc = Doc("virtual.txt",
                contents=contents,
                wrapper=wrapper)
        artifact = doc.artifacts[0]
        assert artifact.__class__.__name__ == "InitialVirtualArtifact"
        assert artifact.data_class_alias() == 'sectioned'

def test_create_working_dir():
    with wrap() as wrapper:
        c1 = Doc("data.txt", contents="12345.67", wrapper=wrapper)
        c2 = Doc("mymod.py", contents="FOO='bar'", wrapper=wrapper)
        doc = Doc("example.py|py",
                c1, c2,
                wrapper=wrapper,
                contents="""\
with open("data.txt", "r") as f:
    print f.read()

import mymod
print mymod.FOO

import os
print sorted(os.listdir(os.getcwd()))
""")

        wrapper.run_docs(doc)

        assert doc.output().data() == """12345.67
bar
['data.txt', 'example.py', 'mymod.py', 'mymod.pyc']
"""
