#! /usr/bin/env python3

# Set globals:
import pandas
import concurrent.futures
import json
import importlib
import shutil
import sys
import os

# ====== TESTS SPECIFICATION ======
# this is not the final test set on Gradescope
# For Coursework1

MODULE = "cwk1"
THIS_FILE = "cwk1_tests.py"

TESTS_VERSION = "14 October 2026"

SHOW_TEST_CALL = True
SHOW_TEST_RESULT = True
SHOW_TEST_ANSWER = True

# You can set a timeout time for each test.
TIMEOUT_SECONDS = 30
   
MOVIES_TEST = {
    "The Matrix": [3, ["sci-fi", "action"]], 
    "Inception": [4, ["sci-fi", "action", "mind-bending"]],
    "Toy Story": [2, ["animation", "family"]], 
    "Spirited Away": [4, ["animation", "fantasy"]],
    "The Godfather": [5, ["drama", "crime"]],
    "Pulp Fiction": [4, ["drama", "crime"]],
    "Interstellar": [5, ["sci-fi", "drama", "space"]],
    "Parasite": [6, ["drama", "thriller"]],
    "The Dark Knight": [7, ["action", "crime", "drama"]],
    "Spider-Man: Into the Spider-Verse": [8, ["animation", "action", "sci-fi"]],
    "Get Out": [9, ["horror", "mystery", "thriller"]],
    "Whiplash": [10, ["drama", "music"]],
    "Grand Budapest Hotel": [11, ["comedy", "adventure"]],
    "Alien": [12, ["sci-fi", "horror"]],
    "Paddington 2": [13, ["animation", "family", "comedy"]],
    "Everything Everywhere All at Once": [14, ["sci-fi", "action", "comedy", "mind-bending"]]
    }

WORD_TEST1 = {"cat", "dog", "elephant", "bear"}
WORD_TEST2 = {"python"}
WORD_TEST3 = {"algorithm", "array", "binary", "boolean", "class", 
    "compiler", "data", "database", "dictionary", "function", 
    "graph", "hash", "heap", "index", "iteration", 
    "list", "loop", "matrix", "memory", "object", 
    "pointer", "queue", "recursion", "search", "set", 
    "sort", "stack", "string", "tree", "variable"}

TESTS = {
    "available_movie_tags":
    [
        ("__M__.available_movie_tags(2, MOVIES_TEST)",
         "eq_list", ['animation', 'family'], 1),
        ("__M__.available_movie_tags(3, MOVIES_TEST)",
         "eq_list", ['action', 'animation', 'family', 'sci-fi'], 1),
        ("__M__.available_movie_tags(6, MOVIES_TEST)",
         "eq_list", ['action', 'animation', 'crime', 'drama', 'family', 'fantasy', 'mind-bending', 'sci-fi', 'space', 'thriller'], 1)
    ],

    "recommend_movies":
    [
    ("__M__.recommend_movies(5, ['sci-fi', 'action'], MOVIES_TEST)",
    "eq_list", [['Inception', 4, ['sci-fi', 'action', 'mind-bending']], ['The Matrix', 3, ['sci-fi', 'action']]], 1),
         
    ("__M__.recommend_movies(5, ['sci-fi', 'mind-bending'], MOVIES_TEST)",
    "eq_list", [['Inception', 4, ['sci-fi', 'action', 'mind-bending']]], 1),
        
    ("__M__.recommend_movies(7, ['crime', 'drama'], MOVIES_TEST)",
    "eq_list", [['The Dark Knight', 7, ['action', 'crime', 'drama']], ['The Godfather', 5, ['drama', 'crime']], ['Pulp Fiction', 4, ['drama', 'crime']]], 1), 
    ],

    "is_english_word":
    [
        ('__M__.is_english_word("I")', "eq_bool", True, 1),
        ('__M__.is_english_word("Python")', "eq_bool", True, 1),
        ('__M__.is_english_word("HelP")', "eq_bool", False,  1),
        ('__M__.is_english_word("Abecedarians")', "eq_bool", True,  1),
        ('__M__.is_english_word("Brexit")', "eq_bool", False, 1),
    ],

    "password_strength":
    [
        ('__M__.password_strength("bananaIsABerry!")', "eq_str", "MEDIUM", 1),
        ('__M__.password_strength("Santo")',  "eq_str", "ILLEGAL", 1),
        ('__M__.password_strength("secret99")', "eq_str", "WEAK", 1),
        ('__M__.password_strength("Secret999!")', "eq_str", "MEDIUM", 1),
        ('__M__.password_strength("7Kings8all9Pies!")', "eq_str", "STRONG", 1)
    ],

    "word_length_summary":
    [
        ('__M__.word_length_summary(WORD_TEST1)', "eq_dict", {'mean_length': 4.5, 'max_length': 8, 'length_distribution': {3: 2, 8: 1, 4: 1}}, 1),
        ('__M__.word_length_summary(WORD_TEST1)', "eq_dict", {'max_length': 8, 'mean_length': 4.5,  'length_distribution': {3: 2, 8: 1, 4: 1}}, 1),
        ('__M__.word_length_summary(WORD_TEST1)', "eq_dict", {'mean_length': 4.5, 'max_length': 8, 'length_distribution': {3: 2, 4: 1, 8: 1}}, 1),
        ('__M__.word_length_summary(WORD_TEST2)',  "eq_dict", {'mean_length': 6.0, 'max_length': 6, 'length_distribution': {6: 1}}, 1),
        ('__M__.word_length_summary(WORD_TEST3)', 
         "eq_dict", {'mean_length': 6.0, 'max_length': 10, 'length_distribution': {5: 6, 4: 7, 9: 3, 6: 6, 8: 4, 7: 2, 10: 1, 3: 1}}, 1),
    ]

}

CHECK_TYPES = {
    "equal": lambda x, y: (type(x) == type(y) and x == y),
    "eq_bool": lambda x, y: (type(x) == bool and type(y) == bool and x == y),
    "eq_int": lambda x, y: (type(x) == int and type(y) == int and x == y),
    "eq_str": lambda x, y: (type(x) == str and type(y) == str and x == y),
    "eq_list": lambda x, y: (type(x) == list and type(y) == list and x == y),
    "eq_dict": lambda x, y: (type(x) == dict and type(y) == dict and x == y),
    "eq_df": lambda x, y: (type(x) == pandas.DataFrame and
                           type(y) == pandas.DataFrame and x.equals(y))
}


# ====== TESTING FUNCTIONS ======
VERSION = 3.0

def tests_version():
    return version()


def version():
    return(("Autograder:", VERSION), ("Tests:", TESTS_VERSION))


# The next two classes are for timeout on the test function calls

class TimeoutError(Exception):
    def __init__(self, message):
        super().__init__(message)


def eval_wrapper(c, fn, f, m):
    # print("In eval wrapper")
    c = c.replace(fn, "__fvar__")
    __fvar__ = f
    if m:
        __M__ = m
    try:
        result = eval(c)
    except BaseException as e:
        result = e
    return result


def eval_with_function_def(timeout, code, fname, func, module=None):

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(eval_wrapper, code, fname, func, module)
        try:
            # print("Getting result ...")
            result = future.result(timeout=10)
            # print("Result:", result)
            return result
        except concurrent.futures.TimeoutError as e:
            # print("Timed out")
            raise TimeoutError(
                "!!! EXCEPTION: Reached time limit: {}s".format(timeout))
        except BaseException as e:
            print("Exception raised:", type(e))
            raise e


def testset_total_marks():
    total = 0
    for f in TESTS:
        total += sum([t[3] for t in TESTS[f]])
    return total


def do_tests(f):
    if os.path.exists("__autograde_test.lock"):
        return None

    def dummy(): pass  # this is just used to check whether f is a function

    if not type(f) == type(dummy):
        print("!!! ERROR: argument should be a function/list of functions")
        return (0, 0)

    fname = f.__name__
    print("*Autograder (v{})*".format(VERSION))
    print("Testing function:", fname)
    
    if fname in TESTS:
        testset = TESTS[fname]
    else:
        print("!!! No tests defined for:", fname)
        return None

    testset_total = 0
    testset_mark = 0
    for test in testset:
        call, checktype, ans, marks = test
        testset_total += marks
        call = call.replace("__M__.", '')
        if SHOW_TEST_CALL:
            print("Evaluating:", call, "...")
        else:
            print("Evaluating:", "***test hidden***", "...")

        try:
            result = eval_with_function_def(TIMEOUT_SECONDS, call, fname, f)
        except TimeoutError:
            print("!!! TIMEOUT -- test took too long!")
            print("!   The test was terminated after {} seconds".
                  format(TIMEOUT_SECONDS))
            print("!   Marks: 0  (of {})".format(marks))
            continue
        except Exception as e:
            print("!!! An ERROR occurred when running this test.")
            print("    The following exception occurred:")
            print("   ", e)
            print("!   Marks: 0  (of {})".format(marks))
            continue

        if SHOW_TEST_RESULT:
            print("Returned:", result.__repr__())
        else:
            print("Returned:", "***result hidden***")

        if SHOW_TEST_ANSWER:
            print("Expected answer:", ans.__repr__())

        is_correct = CHECK_TYPES[checktype](result, ans)
        markstr = "mark" if marks <= 1 else "marks"
        if is_correct:
            print("CORRECT :)   ", marks, markstr)
            testset_mark += marks
        else:
            print("Inorrect :(   (worth {} {})".format(marks, markstr))
    output = ("Total mark for '{}' is {} out of {}"
              .format(fname, testset_mark, testset_total))
    print("-" * len(output))
    print(output)
    print("-" * len(output))
    return None

# --------------------------------------------------------------------------

def do_all_tests(*args, output_file=None):
    if os.path.exists("__autograde_test.lock"):
        # print("Skipping embedded do_all_tests
        # (found __autograde_test.lock file)" )
        return None

    print("Running tests for module:", MODULE)
    print()

    if output_file:
        print("Will write test output to file {} ...".format(output_file))
        original_stdout = sys.stdout
        out = open(output_file, "w")
        sys.stdout = out
        print("<H1>* Autograder *</H1>")
        print("Running tests for module: <b>{}</b><tt>".format(MODULE))

    try:
        try:
            file_to_test = get_file_to_test(MODULE)
            if not file_to_test:
                print("!!! ERROR: no input file found. Exiting checker !!!")
                return False
            import_file = get_import_file(file_to_test)

        except Exception as e:
            print("!!! ERROR: could not find import file ")
            print("(or extract from notebook) !!!")
            print("           the following exception occurred:\n", e)
            return False

        if import_file:
            add_extra_defs(import_file)
            total_mark = test_import_file(import_file)
        else:
            total_mark = False
        return total_mark

    except Exception as e:
        print("!!! ERROR: an exception occured during import or testing !!!")
        print("           the following exception occurred:\n", e)
        return False

    finally:
        if output_file:
            # print( "Restoring stdout" )
            # print("</pre>")
            out.close()
            sys.stdout = original_stdout
            print("Restored stdout")


def add_extra_defs(import_file):
    print("Adding extra defs to:", import_file)
    with open(import_file) as f:
        contents = f.read()
    contents = """
    def display(x):
        pass

    class DummyIpython:
        def system(self,_):
            pass
        def set_next_input(self,_):
            pass
        def run_line_magic(self,_1,_2):
            pass

    def get_ipython():
        return DummyIpython()
    """ + contents
    with open(import_file, "w") as f:
        f.write(contents)


def test_import_file(python_file):

    print("Importing module to be tested ...")

    with open("__autograde_test.lock", "w") as f:
        f.write("PLEASE DELETE THIS FILE")
        f.write("This is a temporary lock file created by BB Autograder.")
        f.write("It prevents test functions begin called while a test is")
        f.write("already in progress, which would cause an infinite loop).")
        f.write("It should be automatically deleted after each test run.")
        f.write("If it has somehow not been deleted please delete it,")
        f.write("otherwise calls to test functions will be blocked.")

    original_stdout = sys.stdout
    sys.stdout = open("tmp.out", "w")
    try:
        __M__ = importlib.import_module(python_file[:-3])

        sys.stdout.close()
        sys.stdout = original_stdout
    except Exception as e:
        sys.stdout.close()
        sys.stdout = original_stdout
        feedback("!!! An ERROR occurred while loading file", python_file)
        feedback("    The following exception occurred:")
        feedback("   ",  e)
        return False
    finally:
        if os.path.exists("__autograde_test.lock"):
            os.remove("__autograde_test.lock")

    print("* import successful *")
    print("Executing tests ...\n\n")

    all_tests_mark = 0

    for fname in TESTS:
        print("Testing:", fname)

        testset = TESTS[fname]
        testset_mark = 0
        testset_total = 0
        for test in testset:
            call, checktype, ans, marks = test
            testset_total += marks
            call_output = call.replace("__M__.", "")
            if SHOW_TEST_CALL:
                print("Evaluating:", call_output, "...")
            else:
                print("Evaluating:", "***test hidden***", "...")

            try:
                result = eval_with_function_def(TIMEOUT_SECONDS,
                                                call, "__@XX@__", None,
                                                module=__M__)
            except TimeoutError:
                print("!!! TIMEOUT -- test took too long!")
                print("!   The test was terminated after {} seconds".
                      format(TIMEOUT_SECONDS))
                print("!   Marks: 0  (of {})".format(marks))
                continue
            except Exception as e:
                print("!!! An ERROR occurred when running this test.")
                print("    The following exception occurred:")
                print("   ", e)
                print("!   Marks: 0  (of {})".format(marks))
                continue

            if SHOW_TEST_RESULT:
                print("Returned:", result.__repr__())
            else:
                print("Returned:", "***result hidden***")

            if SHOW_TEST_ANSWER:
                print("Expected Answer:", ans.__repr__())

            is_correct = CHECK_TYPES[checktype](result, ans)
            markstr = "mark" if marks <= 1 else "marks"
            if is_correct:
                print("CORRECT :)   ", marks, markstr)
                testset_mark += marks
            else:
                print("Inorrect :(   (worth {} {})".format(marks, markstr))
        print("Total for '{}' is {} out of {}\n----\n"
              .format(fname, testset_mark, testset_total))
        all_tests_mark += testset_mark

    print("* Tests completed *\n")
    all_tests_total = testset_total_marks()
    print("TOTAL MARK = {}    (out of {})\n".format(
        all_tests_mark, all_tests_total))
    final_comment = get_final_comment(all_tests_mark, all_tests_total)
    if GRADESCOPE:
        final_comment = "<h3>" + final_comment + "</h3>"
    print(final_comment + '\n')
    return all_tests_mark


def feedback(*args):
    print(*args)


def get_file_to_test(stem):
    in_submission_subdir = False
    if GRADESCOPE and os.path.exists("submission"):
        os.chdir("submission")
        in_submission_subdir = True

    nbname = stem + ".ipynb"
    pyname = stem + ".py"

    if os.path.exists(nbname):
        if os.path.exists(pyname):
            print("!!! WARNING: Found both", nbname, "and", pyname)
            nb_mtime = os.path.getmtime(nbname)
            py_mtime = os.path.getmtime(pyname)
            latest = (nbname if nb_mtime > py_mtime else pyname)
            print("    Will check the most recently modified:", latest)
            test_file = latest
        else:
            test_file = nbname
    else:
        if os.path.exists(pyname):
            test_file = pyname
        else:
            print("!!! ERROR: Did not find input file !!!")
            print("    Was expecting", nbname, "or", pyname)
            if in_submission_subdir:
                os.chdir('..')
                in_submission_subdir = False
            return None
    if in_submission_subdir:
        shutil.copyfile(test_file, "../" + test_file)
        
        try:
            submission_files = os.listdir()
            above_files = os.listdir('..')
            for file in submission_files:
                if file not in above_files:
                    if os.path.isfile(file):
                        shutil.copy(file, '..')
                    elif os.path.isdir(file):
                        shutil.copytree(file, '../' + file)
        except:
            print("!!! WARNING: Something went wrong while moving ")
            print(" additional submitted files.")

        os.chdir('..')
        in_submission_subdir = False
    return test_file



def get_import_file(submitted_filename):
    if submitted_filename.endswith(".py"):
        return submitted_filename

    if submitted_filename.endswith(".ipynb"):
        print("Extracting Python from", submitted_filename, "...")
        import nbformat
        from nbconvert import PythonExporter

        def notebook2python(notebookPath, pythonPath):
            with open(notebookPath) as fh:
                nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)
            exporter = PythonExporter()
            source, meta = exporter.from_notebook_node(nb)
            with open(pythonPath, 'w') as fh:
                fh.writelines(source)

        import_file = submitted_filename[0:-6] + "_from_nb.py"

        try:
            notebook2python(submitted_filename, import_file)

        except Exception as e:
            print("!!! ERROR: could not extract from", submitted_filename)
            print("    The following exception occurred:\n", e)
            return(False)

        return import_file


def get_final_comment(marks, total):
    percent = (marks/total)*100
    if percent <= 50:
        return ("You are advised to revisit this coursework and ask\n"
            "for help regarding any difficulties you are having.")
    
    return "Achieved over the passing mark of 50/100"


def save_results_json(mark, feedback_file, json_file=MODULE +
                      "_bb_autograder_results.json"):
    with open(feedback_file) as f:
        feedback_text = f.read()
    feedback_text = feedback_text.replace("\n\n", "<p>")
    feedback_text = feedback_text.replace("\n", "<br>")

    results = {}
    results["score"] = mark
    results["output"] = feedback_text
    results["visibility"] = "after_due_date"  # Optional visibility setting
    results["stdout_visibility"] = "hidden"
    results["extra_data"] = {}  # Optional extra data to be stored
    with open(json_file, 'w') as jsf:
        json.dump(results, jsf)


GRADESCOPE = False


def __gradescope():
    global GRADESCOPE
    GRADESCOPE = True
    print("Running in Gradescope")

    if not os.path.exists(THIS_FILE):
        # then copy all files from source to root
        shutil.copyfile("source/" + THIS_FILE, "./" + THIS_FILE)
        print("Moving files from source:")
        source_files = os.listdir("source")
        for f in source_files:
            if f == "__pycache__":
                continue
            if os.path.isfile("source/" + f):
                shutil.copyfile("source/" + f, "./" + f)
            if os.path.isdir("source/" + f):
                shutil.copytree("source/" + f, './' + f)

    initialise_globals()

    feedback_file = MODULE + "_bb_autograder_feedback.txt"
    mark = 0
    try:
        mark = do_all_tests(output_file=feedback_file)
    except Exception as e:
        print("!!! Autograder ERROR !!!")
        print("    The exception generated was:\n", e)

    if not os.path.exists(feedback_file):
        print("!!! NO FEEDBACK FILE FOUND !!!")
        with output(feedback_file, "w") as f:
            f.write("!!! ERROR: no feedback report found !!!")

    if mark is False or mark is None:
        mark = 0

    print("Saving json results to 'results/results.json'")
    if not os.path.exists('results'):
        os.mkdir('results')
    save_results_json(mark, feedback_file, json_file="results/results.json")


def main():
    initialise_globals()
    mark = do_all_tests(output_file=None)


DO_MAIN = True
if __name__ == "__main__" and DO_MAIN:
    main()

DO_MAIN = True
if __name__ == "__main__" and DO_MAIN:
    main()

DO_MAIN = True
if __name__ == "__main__" and DO_MAIN:
    main()
