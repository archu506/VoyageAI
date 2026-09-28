# Patch SQLAlchemy TypingOnly for Python 3.13+ compatibility
try:
    import sqlalchemy.util.langhelpers as lh
    if hasattr(lh, 'TypingOnly'):
        original_init_subclass = lh.TypingOnly.__init_subclass__
        def patched_init_subclass(cls, *args, **kwargs):
            try:
                if hasattr(original_init_subclass, '__func__'):
                    original_init_subclass.__func__(cls, *args, **kwargs)
                else:
                    original_init_subclass(cls, *args, **kwargs)
            except AssertionError:
                pass
        lh.TypingOnly.__init_subclass__ = classmethod(patched_init_subclass)
except Exception:
    pass
