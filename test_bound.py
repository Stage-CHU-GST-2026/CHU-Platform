class A:
    def _run(self, x):
        return f"A({x})"

a = A()
original_run = a._run

def safe_run(*args, _orig=original_run, **kwargs):
    print("args:", args)
    return _orig(*args, **kwargs)

a._run = safe_run
print(a._run(10))
