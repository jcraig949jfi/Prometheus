function techne_run_script(fname)
% Techne harness: run a MATLAB-style script that defines its local functions AFTER the body.
% Octave defines script-local functions only when execution reaches the definition, so the
% functions block is evaluated first (as command-line function definitions), then the body.
% The fossil file is read, never written. Variables land in the caller's workspace.
  txt = fileread(fname);
  k = regexp(txt, '(?m)^\s*function\s', 'once');
  if isempty(k)
    body = txt; funcs = '';
  else
    body = txt(1:k-1); funcs = txt(k:end);
  end
  if ~isempty(funcs)
    evalin('base', funcs);
  end
  evalin('base', body);
end
