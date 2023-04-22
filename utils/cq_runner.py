import cadquery as cq
from contextlib import contextmanager


@contextmanager
def ShowObjectTracker():
    ShowObjectTracker.called = False
    try:
        yield
    finally:
        pass


def save(result, stl_file_path):
    ShowObjectTracker.called = True
    cq.exporters.export(result, stl_file_path, "STL")


def run_cadquery(script, stl_file_path):
    # Basically this runs the cadquery script in a sandboxed environment and saves the result to a file
    # if the script doesn't call show_object explicitly (which is the case for most scripts) it will
    # save the last workplane object in the namespace
    # TODO: write a secure version of this function
    namespace = {"cq": cq, "show_object": lambda result: save(result, stl_file_path)}
    print(f"Running script {script} and saving to {stl_file_path} ...")
    print("Do not run this function in a live environment with untrusted code. It is not secure.")
    with ShowObjectTracker():
        try:
            exec(script, namespace)
        except Exception as e:
            print(f"Error while executing the script: {e}")
            return

        if not ShowObjectTracker.called:
            for name, value in namespace.items():
                if isinstance(value, cq.Workplane):
                    save(value, stl_file_path)