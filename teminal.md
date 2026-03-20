# Đây là terminal log của python nhé:
File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:42.846 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:42.847 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
_locate_stream(Workbook): seen
    0  5 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
   20  4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
  100= 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
  120  4 4 3 2
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
_locate_stream(Workbook): seen
    0  5 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
   20  4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
  140= 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
  160  4 4 4 4 3 2 2
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
_locate_stream(Workbook): seen
    0  5 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
   20  4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
  180= 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
  200  4 4 4 4 4 4 3 2 2
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
_locate_stream(Workbook): seen
    0  5 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
   20  4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
  160= 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
  180  4 4 4 4 4 4 4 4 4 4 4 4 4 4 3 2 2
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
_locate_stream(Workbook): seen
    0  5 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
   20  4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
  140= 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
  160  4 4 3 2 2
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
[DEBUG] Header region: rows 0-5, Data starts at row 5
[DEBUG] No classification columns detected in header region
2026-03-19 21:31:43.168 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 703, in render_commitments
    avg_str = row[2].text_input("", key=f"avg_{subj}", label_visibility="collapsed", placeholder="-")
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.170 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 703, in render_commitments
    avg_str = row[2].text_input("", key=f"avg_{subj}", label_visibility="collapsed", placeholder="-")
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.172 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 703, in render_commitments
    avg_str = row[2].text_input("", key=f"avg_{subj}", label_visibility="collapsed", placeholder="-")
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.175 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 703, in render_commitments
    avg_str = row[2].text_input("", key=f"avg_{subj}", label_visibility="collapsed", placeholder="-")
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.178 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 703, in render_commitments
    avg_str = row[2].text_input("", key=f"avg_{subj}", label_visibility="collapsed", placeholder="-")
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.180 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 703, in render_commitments
    avg_str = row[2].text_input("", key=f"avg_{subj}", label_visibility="collapsed", placeholder="-")
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.182 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 703, in render_commitments
    avg_str = row[2].text_input("", key=f"avg_{subj}", label_visibility="collapsed", placeholder="-")
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.185 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.186 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.187 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.189 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.191 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.191 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.194 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.195 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.196 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.198 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.199 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.200 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.202 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.203 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
2026-03-19 21:31:43.204 `label` got an empty value. This is discouraged for accessibility reasons and may be disallowed in the future by raising an exception. Please provide a non-empty label and hide it with label_visibility if needed.
Stack (most recent call last):
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1075, in _bootstrap_inner       
    self.run()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 379, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 705, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 129, in exec_func_with_error_handling
    result = func()
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 689, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
  File "D:\coding\qlcl\app\main.py", line 897, in <module>
    main()
  File "D:\coding\qlcl\app\main.py", line 891, in main
    render_commitments()
  File "D:\coding\qlcl\app\main.py", line 715, in render_commitments
    val_str = row[col_idx].text_input("", key=f"{key_suffix}_{subj}", label_visibility="collapsed", placeholder="0")  
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\runtime\metrics_util.py", line 532, in wrapped_func
    result = non_optional_func(*args, **kwargs)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 322, in text_input
    return self._text_input(
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\widgets\text_widgets.py", line 371, in _text_input
    maybe_raise_label_warnings(label, label_visibility)
  File "C:\Users\Nhan\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamlit\elements\lib\policies.py", line 187, in maybe_raise_label_warnings
    _LOGGER.warning(
