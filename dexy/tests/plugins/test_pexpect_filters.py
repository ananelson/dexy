from dexy.doc import Doc
from dexy.tests.utils import assert_in_output
from dexy.tests.utils import wrap
from nose.exc import SkipTest

RUST = """fn main() {
    io::println("hello?");
}"""

def test_rust_interactive():
    raise SkipTest()
    with wrap() as wrapper:
        doc = Doc("example.rs|rusti",
                wrapper,
                [],
                contents = "1+1"
                )
        wrapper.run(doc)
        assert "rusti> 1+1\n2" in str(doc.output_data())

def test_rust():
    with wrap() as wrapper:
        doc = Doc("example.rs|rustc",
                wrapper,
                [],
                contents = RUST
                )
        wrapper.run(doc)
        assert str(doc.output_data()) == "hello?\n"

PYTHON_CONTENT = """
x = 6
y = 7
"""
def test_python_filter_record_vars():
    with wrap() as wrapper:
        doc = Doc("example.py|pycon",
                wrapper,
                [],
                pycon = { 'record-vars' :  True},
                contents = PYTHON_CONTENT
                )

        wrapper.run(doc)
        assert "doc:example.py-vars.json" in wrapper.nodes

def test_matlab_filter():
    assert_in_output('matlabint', "fprintf (1, 'Hello, world\\n')\n", "< M A T L A B (R) >")

def test_clj_filter():
    assert_in_output('cljint', '1+1', "user=> 1+1")

def test_ksh_filter():
    assert_in_output('kshint', 'ls', "example.txt")

def test_php_filter():
    assert_in_output('phpint', '1+1', "php > 1+1")

def test_rhino_filter():
    assert_in_output('rhinoint', '1+1', "js> 1+1")

def test_irb_filter():
    assert_in_output('irb', "puts 'hello'", ">> puts 'hello'")

def test_pycon_filter_single_section():
    assert_in_output('pycon', "print 'hello'", ">>> print 'hello'")

def test_ipython_filter():
    assert_in_output('ipython', "print 'hello'", ">>> print 'hello'")

def test_r_filter():
    assert_in_output('r', '1+1', '> 1+1')

def test_shint_filter():
    with wrap() as wrapper:
        src = """
### @export "touch"
touch newfile.txt

### @export "ls"
ls
"""
        doc = Doc("example.sh|idio|shint|pyg",
                wrapper,
                [],
                contents = src)
        wrapper.run(doc)

        assert doc.output_data().keys() == ['1', 'touch', 'ls']

def test_pycon_filter():
    with wrap() as wrapper:
        src = """
### @export "vars"
x = 6
y = 7

### @export "multiply"
x*y

"""
        node = Doc("example.py|idio|pycon",
                wrapper,
                [],
                contents=src)

        wrapper.run(node)

        assert node.output_data().keys() == ['1', 'vars', 'multiply']
        assert node.output_data().as_sectioned()['vars'] == """
>>> x = 6
>>> y = 7"""

        assert node.output_data().as_sectioned()['multiply'] == """
>>> x*y
42"""

